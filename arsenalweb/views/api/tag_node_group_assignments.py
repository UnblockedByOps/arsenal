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
from pyramid.view import view_config
from pyramid.response import Response
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    log,
    )
from arsenalweb.views.api import (
    get_api_attribute,
    api_read_by_id,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    TagNodeGroupAssignment,
    )


@view_config(route_name='api_tag_node_group_assignments', request_method='GET', request_param='schema=true', renderer='json')
def api_tag_node_group_assignments_schema(request):
    """Schema document for tag_node_group_assignments API"""

    tag_node_group_assignments = {
    }

    return tag_node_group_assignments


@view_config(route_name='api_tag_node_group_assignment_r', request_method='GET', renderer='json')
def api_tag_node_group_assignment_read_attrib(request):
    """Process read requests for /api/tag_node_group_assignments/{id}/{resource} route matches"""

    return get_api_attribute(request, 'TagNodeGroupAssignment')


@view_config(route_name='api_tag_node_group_assignment', request_method='GET', renderer='json')
def api_tag_node_group_assignment_read_id(request):
    """Process read requests for /api/tag_node_group_assignments/{id} route matches"""

    return api_read_by_id(request, 'TagNodeGroupAssignment')


@view_config(route_name='api_tag_node_group_assignments', request_method='GET', renderer='json')
def api_tag_node_group_assignment_read(request):
    """Process read requests for /api/tag_node_group_assignments route match"""

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        tag_id = request.params.get('tag_id')
        node_group_id = request.params.get('node_group_id')
        exact_get =  request.GET.get("exact_get", None)

        s = ''
        ta = DBSession.query(TagNodeGroupAssignment)
        if any((tag_id, node_group_id)):

            # FIXME: this is starting to get replicated. Can it be a function?
            for k,v in request.GET.items():
                # FIXME: This is sub-par. Need a better way to distinguish
                # meta params from search params without having to
                # pre-define everything.
                if k == 'exact_get':
                    continue

                s+='{0}={1},'.format(k, v)
                if exact_get:
                    log.info('Exact filtering on {0}={1}'.format(k, v))
                    ta = ta.filter(getattr(TagNodeGroupAssignment ,k)==v)
                else:
                    log.info('Loose filtering on {0}={1}'.format(k, v))
                    ta = ta.filter(getattr(TagNodeGroupAssignment ,k).like('%{0}%'.format(v)))

            log.info('Searching for tag_node_group_assignments with params: {0}'.format(s.rstrip(',')))

        else:
            log.info('Displaying all tag_node_group_assignments')

        ta = ta.limit(perpage).offset(offset).all()

        return ta

    except NoResultFound:
            return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error querying api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tag_node_group_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_tag_node_group_assignments_write(request):
    """Process write requests for /api/tag_node_group_assignments route match"""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        try:
            tag_id = payload['tag_id']
            node_group_id = payload['node_group_id']

            log.info('Checking for tag_node_group_assignment tag_id={0}node_group_id={1}'.format(tag_id, node_group_id))
            q = DBSession.query(TagNodeGroupAssignment)
            q = q.filter(TagNodeGroupAssignment.tag_id==tag_id)
            q = q.filter(TagNodeGroupAssignment.node_group_id==node_group_id)
            q.one()
            log.info('tag_node_group_assignment already exists')
            return Response(content_type='application/json', status_int=409)
        except NoResultFound:
            try:
                log.info('Creating new tag_node_group_assignment tag_id={0},node_id={1}'.format(tag_id, node_group_id))
                utcnow = datetime.utcnow()
                ta = TagNodeGroupAssignment(tag_id=tag_id,
                                            node_group_id=node_group_id,
                                            updated_by=au['user_id'],
                                            created=utcnow,
                                            updated=utcnow)
                DBSession.add(ta)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new tag_node_group_assignment tag_id={0},node_group_id={1},exception={2}'.format(tag_id, node_group_id, e))
                raise

    except Exception as e:
        log.error('Error with tag_node_group_assignment API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tag_node_group_assignment', permission='api_write', request_method='DELETE', renderer='json')
def api_tag_node_group_assignments_delete_id(request):
    """Process delete requests for /api/tag_node_group_assignments/{id} route match."""

    return api_delete_by_id(request, 'TagNodeGroupAssignment')


@view_config(route_name='api_tag_node_group_assignments', permission='api_write', request_method='DELETE', renderer='json')
def api_tag_node_group_assignments_delete(request):
    """Process delete requests for /api/tag_node_group_assignments route match.
       Iterates over passed parameters."""

    return api_delete_by_params(request, 'TagNodeGroupAssignment')
