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
    api_read_by_params,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    NodeGroup,
    )


@view_config(route_name='api_node_groups', request_method='GET', request_param='schema=true', renderer='json')
def api_node_groups_schema(request):
    """Schema document for the node_groups API."""

    ng = {
    }

    return ng


@view_config(route_name='api_node_group_r', request_method='GET', renderer='json')
def api_node_group_read_attrib(request):
    """Process read requests for the /api/node_groups/{id}/{resource} route."""

    return get_api_attribute(request, 'NodeGroup')


@view_config(route_name='api_node_group', request_method='GET', renderer='json')
def api_node_group_read_id(request):
    """Process read requests for the /api/node_groups/{id} route."""

    return api_read_by_id(request, 'NodeGroup')


@view_config(route_name='api_node_groups', request_method='GET', renderer='json')
def api_node_group_read(request):
    """Process read requests for the /api/node_groups route."""
    
    return api_read_by_params(request, 'NodeGroup')


@view_config(route_name='api_node_groups', permission='api_write', request_method='PUT', renderer='json')
def api_node_groups_write(request):
    """Process write requests for /api/node_groups route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        node_group_name = payload['node_group_name']
        node_group_owner = payload['node_group_owner']
        node_group_description = payload['node_group_description']

        log.debug('Searching for node_group node_group_name={0}'.format(node_group_name))

        try:
            ng = DBSession.query(NodeGroup)
            ng = ng.filter(NodeGroup.node_group_name==node_group_name)
            ng = ng.one()
        except NoResultFound:
            try:
                log.info('Creating new node_group node_group_name={0},node_group_owner={1},description={2}'.format(node_group_name, node_group_owner, node_group_description))
                utcnow = datetime.utcnow()

                ng = NodeGroup(node_group_name=node_group_name,
                               node_group_owner=node_group_owner,
                               description=node_group_description,
                               updated_by=au['user_id'],
                               created=utcnow,
                               updated=utcnow)

                DBSession.add(ng)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, node_group_description, e))
                raise
        else:
            try:
                log.info('Updating node_group node_group_name={0}'.format(node_group_name))

                ng.node_group_name = node_group_name
                ng.node_group_owner = node_group_owner
                ng.description = node_group_description
                ng.updated_by=au['user_id']

                DBSession.flush()
            except Exception as e:
                log.error('Error updating node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, node_group_description, e))
                raise

        return ng

    except Exception as e:
        log.error('Error writing to node_groups API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_group', permission='api_write', request_method='DELETE', renderer='json')
def api_node_groups_delete_id(request):
    """Process delete requests for the /api/node_groups/{id} route."""

    return api_delete_by_id(request, 'NodeGroup')


@view_config(route_name='api_node_groups', permission='api_write', request_method='DELETE', renderer='json')
def api_node_groups_delete(request):
    """Process delete requests for the /api/node_groups route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'NodeGroup')
