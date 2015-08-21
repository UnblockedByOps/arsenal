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
import json
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    log,
    _api_get,
    _api_put,
    )
from arsenalweb.views.api import (
    get_api_attribute,
    api_read_by_id,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    Status,
    )


@view_config(route_name='api_nodes', request_method='GET', request_param='schema=true', renderer='json')
def api_node_schema(request):
    """Schema document for nodes API"""

    log.debug('schema requested')

    node = {
    }

    return node


@view_config(route_name='api_node_r', request_method='GET', renderer='json')
def api_node_read_attrib(request):
    """Process read requests for the /api/nodes/{id}/{resource} route."""

    return get_api_attribute(request, 'Node')


@view_config(route_name='api_node', request_method='GET', renderer='json')
def api_node_read_id(request):
    """Process read requests for the /api/nodes/{id} route."""

    return api_read_by_id(request, 'Node')


@view_config(route_name='api_nodes', request_method='GET', renderer='json')
def api_node_read(request):
    """Process read requests for the /api/nodes route."""

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone("start"))
    except:
        pass

    try:
        exact_get =  request.GET.get("exact_get", None)

        if request.params:
            s = ''
            # Filter on all the passed in terms
            q = DBSession.query(Node)

            for k,v in request.GET.items():
                # FIXME: This is sub-par. Need a better way to distinguish 
                # meta params from search params without having to
                # pre-define everything.
                if k == 'unique_id':
                    v = v.lower()
                if k == 'exact_get':
                    continue

                s+='{0}={1},'.format(k, v)    
                if exact_get:
                    log.debug('Exact filtering on {0}={1}'.format(k, v))
                    q = q.filter(getattr(Node ,k)==v)
                else:
                    log.debug('Loose filtering on {0}={1}'.format(k, v))
                    q = q.filter(getattr(Node ,k).like('%{0}%'.format(v)))

            log.debug('Searching for node {0}'.format(s.rstrip(',')))

            nodes = q.all()
            return nodes
        else:

            log.debug('Displaying all nodes')

            n = DBSession.query(Node)
            return n.limit(perpage).offset(offset).all()

    # FIXME: Should AttributeError return something different?
    except (NoResultFound, AttributeError):
        return Response(content_type='application/json', status_int=404)

    except Exception, e:
        log.error('Error reading from nodes API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node', permission='api_write', request_method='PUT', renderer='json')
def api_node_write_id(request):
    """Process write requests for the /api/nodes/{id} route."""

    au = get_authenticated_user(request)

    try:
        node_id = request.matchdict['id']
        payload = request.json_body

        s = ''
        for k,v in payload.items():
            s+='{0}={1},'.format(k, v)

        log.info('Updating node_id: {0} params: {1}'.format(node_id, s.rstrip(',')))

        n = DBSession.query(Node)
        n = n.filter(Node.node_id==node_id)
        n = n.one()

        # FIXME: Do we want to limit anything here? Keys that don't exist will
        # be ignored, keys that can't be set with throw an error. Doesn't
        # feel right though to just accept what's put to the endpoint.
        for k,v in payload.items():
            setattr(n ,k, v)

        n.updated_by=au['user_id']
        DBSession.flush()

    except Exception as e:
        log.error('Error writing to nodes API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)

    return n


@view_config(route_name='api_nodes', permission='api_write', request_method='PUT', renderer='json')
def api_node_write(request):
    """Process write requests for the /api/nodes route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        # FIXME: right now /api/nodes expects all paramters to be passed, no piecemeal updates. Also no support for bulk updates
        if payload['register']:

            # Get the hardware_profile_id or create if it doesn't exist.
            try:
                manufacturer = payload['hardware_profile']['manufacturer']
                model = payload['hardware_profile']['model']

                uri = '/api/hardware_profiles'
                data = {'manufacturer': manufacturer,
                        'model': model
                }
                hardware_profile = _api_get(request, uri, data)

                if not hardware_profile:

                    log.debug('hardware_profile not found, creating')

                    data_j = json.dumps(data, default=lambda o: o.__dict__)
                    _api_put(request, uri, data=data_j)
                    hardware_profile = _api_get(request, uri, data)

                hardware_profile_id = hardware_profile['hardware_profile_id']
                log.debug('hardware_profile is: {0}'.format(hardware_profile))

            except Exception as e:
                log.error('Unable to determine hardware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
                raise

            # Get the operating_system_id or create if it doesn't exist.
            try:
                variant = payload['operating_system']['variant']
                version_number = payload['operating_system']['version_number']
                architecture = payload['operating_system']['architecture']
                description = payload['operating_system']['description']

                uri = '/api/operating_systems'
                data = {'variant': variant,
                        'version_number': version_number,
                        'architecture': architecture,
                        'description': description
                }
                operating_system = _api_get(request, uri, data)

                if not operating_system:
    
                    log.debug('operating_system not found, attempting to create')

                    data_j = json.dumps(data, default=lambda o: o.__dict__)
                    _api_put(request, uri, data=data_j)
                    operating_system = _api_get(request, uri, data)

                operating_system_id = operating_system['operating_system_id']
                log.info('operating_system is: {0}'.format(operating_system))

            except Exception as e:
                log.error('Unable to determine operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
                raise

            try:
                unique_id = payload['unique_id'].lower()
                node_name = payload['node_name']
                uptime = payload['uptime']

                log.debug('Searching for node unique_id={0}'.format(unique_id))
                n = DBSession.query(Node)
                n = n.filter(Node.unique_id==unique_id)
                n = n.one()
            except NoResultFound:
                try:
                    log.info('Creating new node node_name={0},unique_id={1}'.format(node_name, unique_id))
                    utcnow = datetime.utcnow()

                    n = Node(unique_id=unique_id,
                             node_name=node_name,
                             hardware_profile_id=hardware_profile_id,
                             operating_system_id=operating_system_id,
                             uptime=uptime,
                             status_id=2,
                             updated_by=au['user_id'],
                             created=utcnow,
                             updated=utcnow)

                    DBSession.add(n)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error creating new node node_name={0},unique_id={1},exception={2}'.format(node_name, unique_id, e))
                    raise
            else:
                try:
                    log.info('Updating node: {0}'.format(unique_id))

                    n.node_name = node_name
                    n.hardware_profile_id = hardware_profile_id
                    n.operating_system_id = operating_system_id
                    n.uptime = uptime
                    n.updated_by=au['user_id']

                    DBSession.flush()
                except Exception as e:
                    log.error('Error updating node node_name={0},unique_id={1},exception={2}'.format(node_name, unique_id, e))
                    raise
        else:

            # Manually created node via the client.
            try:
                node_name = payload['node_name']
                unique_id = payload['unique_id'].lower()
                status_id = payload['node_status_id']

                log.debug('Searching for node unique_id={0}'.format(unique_id))
                n = DBSession.query(Node)
                n = n.filter(Node.unique_id==unique_id)
                n = n.one()
            except NoResultFound:
                try:

                    log.info('Manually creating new node node_name={0},unique_id={1}'.format(node_name, unique_id))
                    utcnow = datetime.utcnow()

                    n = Node(node_name=node_name,
                             unique_id=unique_id,
                             status_id=status_id,
                             updated_by=au['user_id'],
                             created=utcnow,
                             updated=utcnow)

                    DBSession.add(n)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error creating new node node_name={0}unique_id={1},status_id={2},exception={3}'.format(node_name, unique_id, status_id, e))
                    raise
            else:
                try:
                    log.info('Updating node node_name={0},unique_id={1}'.format(node_name, unique_id))

                    n.node_name = node_name
                    n.status_id = status_id
                    n.updated_by=au['user_id']

                    DBSession.flush()
                except Exception as e:
                    log.error('Error updating node node_name={0},unique_id={1},exception={2}'.format(node_name, unique_id, e))
                    raise

        return n

    except Exception as e:
        log.error('Error writing to nodes API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node', permission='api_write', request_method='DELETE', renderer='json')
def api_nodes_delete_id(request):
    """Process delete requests for the /api/nodes/{id} route."""

    return api_delete_by_id(request, 'Node')


@view_config(route_name='api_nodes', permission='api_write', request_method='DELETE', renderer='json')
def api_nodes_delete(request):
    """Process delete requests for the /api/nodes route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'Node')
