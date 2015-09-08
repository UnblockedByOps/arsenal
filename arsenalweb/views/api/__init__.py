#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import re
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from arsenalweb.views import (
    get_authenticated_user,
    log,
    get_pag_params,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    NodeGroup,
    NodeGroupAssignment,
    Status,
    Tag,
    TagNodeAssignment,
    TagNodeGroupAssignment,
    HardwareProfile,
    OperatingSystem,
    HypervisorVmAssignment,
    )


def camel_to_underscore(model_type):
    """Convert camel case to underscore for mapping."""

    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    c = a.sub(r' \1', model_type).lower().strip()
    c = c.replace(" ","_")

    return c


def get_api_attribute(request, model_type):
    """Get single attribute request for /api/{object_type}/{id}/{attribute}
       route match."""

    c = camel_to_underscore(model_type)
    c_id = c + '_id'

    resource_id = request.matchdict['id']
    resource = request.matchdict['resource']
    log.debug('Querying for attribute={0},url={1}'.format(resource, request.url))

    try:
        # FIXME: Something better here than globals?
        q = DBSession.query(globals()[model_type])
        q = q.filter(getattr(globals()[model_type], c_id) == resource_id)
        q = q.one()
        return { resource: getattr(q, resource) }

    except (NoResultFound, AttributeError):
        return Response(content_type='application/json', status_int=404)
    except Exception as e:
        log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
        raise


def api_read_by_id(request, model_type):
    """Process get requests for /api/{object_type}/{id} route match."""

    resource_id = request.matchdict['id']
    c = camel_to_underscore(model_type)
    c_id = c + '_id'

    try:
        log.debug('Displaying single {0} {1}={2}'.format(c, c_id, resource_id))

        # FIXME: Something better here than globals?
        q = DBSession.query(globals()[model_type])
        q = q.filter(getattr(globals()[model_type], c_id) == resource_id)
        q = q.one()

        return q

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error querying {0} url={1},exception={2}'.format(c, request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


def api_read_by_params(request, model_type):
    """Process get requests for /api/{object_type} route match."""

    c = camel_to_underscore(model_type)
    (perpage, offset) = get_pag_params(request)

    try:
        exact_get =  request.GET.get("exact_get", None)

        if request.params:
            s = ''
            # Filter on all the passed in terms
            q = DBSession.query(globals()[model_type])

            for k,v in request.GET.items():
                # Force unique_id to lower since mac addrs can be represented both ways.
                if k == 'unique_id':
                    v = v.lower()
                # FIXME: This is sub-par. Need a better way to distinguish
                # meta params from search params without having to
                # pre-define everything.
                if k == 'exact_get':
                    continue
                if k == 'start':
                    continue

                s+='{0}={1},'.format(k, v)
                if exact_get:
                    log.debug('Exact filtering on {0}={1}'.format(k, v))
                    if ',' in v:
                        q = q.filter(or_(getattr(globals()[model_type] ,k) == t for t in v.split(',')))
                    else:
                        q = q.filter(getattr(globals()[model_type] ,k)==v)
                else:
                    log.debug('Loose filtering on {0}={1}'.format(k, v))
                    if ',' in v:
                        log.info('Multiple values for key {0}={1}'.format(k, v))
                        multior = []
                        for t in v.split(','):
                            multior.append(((getattr(globals()[model_type] ,k).like(('%{0}%'.format(t))))))
                        q = q.filter(or_(*multior))
                    else:
                        q = q.filter(getattr(globals()[model_type] ,k).like('%{0}%'.format(v)))

            log.debug('Searching for {0} {1}'.format(c, s.rstrip(',')))

            total = q.count()
            myob = q.limit(perpage).offset(offset).all()
            results = {'meta': {'total': total}, 'results': myob}
            return results
        else:

            log.info('Displaying all {0}'.format(c))

            q = DBSession.query(globals()[model_type])
            total = q.count()
            myob =  q.limit(perpage).offset(offset).all()
            results = {'meta': {'total': total}, 'results': myob}
            return results

    # FIXME: Should AttributeError return something different?
    except (NoResultFound, AttributeError):
        return Response(content_type='application/json', status_int=404)

    except Exception, e:
        log.error('Error reading from {0} API={1},exception={2}'.format(c, request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


def api_delete_by_id(request, model_type):
    """Process delete requests for /api/{object_type}/{id} route match."""

    # FIXME: Will be used for auditing eventually. Would be nice to use 
    # request.authenticated_userid, but I think this gets ugly when it's
    # an AD user. Need to test.
    au = get_authenticated_user(request)

    resource_id = request.matchdict['id']
    c = camel_to_underscore(model_type)
    c_id = c + '_id'
    c_name = c + '_name'

    try:
        log.debug('Checking for {0}={1}'.format(c_id, resource_id))

        # FIXME: Something better here than globals?
        q = DBSession.query(globals()[model_type])
        q = q.filter(getattr(globals()[model_type], c_id) == resource_id)
        q = q.one()

        object_name = getattr(q, c_name)

        # FIXME: Need auditing
        # FIXME: What about orphaned assigments? Should we clean them up?
        log.info('Deleting {0}={1},{2}={3}'.format(c_name, object_name, c_id, resource_id))
        DBSession.delete(q)
        DBSession.flush()

        return True

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error deleting {0}={1},exception={2}'.format(c_id, resource_id, e))
        return Response(str(e), content_type='application/json', status_int=500)


def api_delete_by_params(request, model_type):
    """Process delete requests for /api/{object_type} route match. Iterates
       over passed parameters."""

    # FIXME: Should we enforce required parameters here?

    # Will be used for auditing
    au = get_authenticated_user(request)

    # FIXME: Should we allow this to be set on the client, or hard code it to true, requiring an # exact match? Might make sense since there is no confirmation, it just deletes.
    exact_get = True
    c = camel_to_underscore(model_type)

    try:
        payload = request.json_body

        s = ''
        q = DBSession.query(globals()[model_type])

        for k,v in payload.items():
            # FIXME: This is sub-par. Need a better way to distinguish
            # meta params from search params without having to
            # pre-define everything.
            if k == 'exact_get':
                continue

            s+='{0}={1},'.format(k, v)
            if exact_get:
                log.debug('Exact filtering on {0}={1}'.format(k, v))
                q = q.filter(getattr(globals()[model_type] ,k)==v)
            else:
                log.debug('Loose filtering on {0}={1}'.format(k, v))
                q = q.filter(getattr(globals()[model_type] ,k).like('%{0}%'.format(v)))
        log.debug('Searching for {0} with params: {1}'.format(c, s.rstrip(',')))

        q = q.one()

        # FIXME: Need auditing
        log.info('Deleting {0} with params: {1}'.format(c, s.rstrip(',')))
        DBSession.delete(q)
        DBSession.flush()

        return True

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error deleting {0} with params: {1} exception: {2}'.format(c, s.rstrip(','), e))
        return Response(str(e), content_type='application/json', status_int=500)


