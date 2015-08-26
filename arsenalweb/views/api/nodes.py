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
    api_read_by_params,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.views.api.hardware_profiles import (
    create_hardware_profile,
    )
from arsenalweb.views.api.operating_systems import (
    create_operating_system,
    )
from arsenalweb.models import (
    DBSession,
    Node,
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

    return api_read_by_params(request, 'Node')


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


@view_config(route_name='api_register', permission='api_register', request_method='PUT', renderer='json')
def api_node_register(request):
    """Process registration requests for the /api/register route."""

    au = get_authenticated_user(request)

    log.info('Registering new node')
    try:
        payload = request.json_body

        # Get the hardware_profile_id or create if it doesn't exist.
        try:
            manufacturer = payload['hardware_profile']['manufacturer']
            model = payload['hardware_profile']['model']

            # FIXME: remove the http call
            uri = '/api/hardware_profiles'
            data = {'manufacturer': manufacturer,
                    'model': model
            }
            hardware_profile = _api_get(request, uri, data)

            try:
                hardware_profile_id = hardware_profile['results'][0]['hardware_profile_id']

            except IndexError:

                log.debug('hardware_profile not found, creating')

                hardware_profile = create_hardware_profile(manufacturer, model, au['user_id'])
                hardware_profile_id = hardware_profile.hardware_profile_id

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

            # FIXME: remove the http call
            uri = '/api/operating_systems'
            data = {'variant': variant,
                    'version_number': version_number,
                    'architecture': architecture,
                    'description': description
            }
            operating_system = _api_get(request, uri, data)

            try:
                operating_system_id = operating_system['results'][0]['operating_system_id']

            except IndexError:

                log.debug('operating_system not found, attempting to create')

                operating_system = create_operating_system(variant, version_number, architecture, description, au['user_id'])
                operating_system_id = operating_system.operating_system_id
            log.debug('operating_system is: {0}'.format(operating_system))

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

        return n

    except Exception as e:
        log.error('Error registering new node API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_nodes', permission='api_write', request_method='PUT', renderer='json')
def api_node_write(request):
    """Process write requests for the /api/nodes route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

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
