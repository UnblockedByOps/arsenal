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
    NodeGroupAssignment,
    )


@view_config(route_name='api_node_group_assignments', request_method='GET', request_param='schema=true', renderer='json')
def api_node_group_assignments_schema(request):
    """Schema document for the node_group_assignments API."""

    nga = {
    }

    return nga


@view_config(route_name='api_node_group_assignment_r', request_method='GET', renderer='json')
def api_node_group_assignment_read_attrib(request):
    """Process read requests for the /api/node_group_assignments/{id}/{resource} route."""

    return get_api_attribute(request, 'NodeGroupAssignment')


@view_config(route_name='api_node_group_assignment', request_method='GET', renderer='json')
def api_node_group_assignment_read_id(request):
    """Process read requests for the /api/node_group_assignments/{id} route."""

    return api_read_by_id(request, 'NodeGroupAssignment')


@view_config(route_name='api_node_group_assignments', request_method='GET', renderer='json')
def api_node_group_assignment_read(request):
    """Process read requests for the /api/node_group_assignments route."""

    return api_read_by_params(request, 'NodeGroupAssignment')


@view_config(route_name='api_node_group_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_node_group_assignments_write(request):
    """Process write requests for the /api/node_group_assignments route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        node_id = payload['node_id']
        node_group_id = payload['node_group_id']

        log.debug('Checking for node_group_assignment node_id={0},node_group_id={1}'.format(node_id, node_group_id))

        try:
            nga = DBSession.query(NodeGroupAssignment)
            nga = nga.filter(NodeGroupAssignment.node_id==node_id)
            nga = nga.filter(NodeGroupAssignment.node_group_id==node_group_id)
            nga = nga.one()
            log.info('node_group_assignment already exists')
            return Response(content_type='application/json', status_int=409)
        except NoResultFound:
            try:
                log.debug('Creating new node_group_assignment for node_id={0},node_group_id={1}'.format(node_id, node_group_id))
                utcnow = datetime.utcnow()

                nga = NodeGroupAssignment(node_id=node_id,
                                          node_group_id=node_group_id,
                                          updated_by=au['user_id'],
                                          created=utcnow,
                                          updated=utcnow)

                DBSession.add(nga)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new node_group_assignment node_id={0},node_group_id={1},exception={2}'.format(node_id, node_group_id, e))
                raise

    except Exception as e:
        log.error('Error writing to node_group_assignment API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_group_assignment', permission='api_write', request_method='DELETE', renderer='json')
def api_node_group_assignments_delete_id(request):
    """Process delete requests for the /api/node_group_assignments/{id} route."""

    return api_delete_by_id(request, 'NodeGroupAssignment')


@view_config(route_name='api_node_group_assignments', permission='api_write', request_method='DELETE', renderer='json')
def api_node_group_assignments_delete(request):
    """Process delete requests for the /api/node_group_assignments route.
       Iterates over passed parameters."""

    return api_delete_by_params(request, 'NodeGroupAssignment')
