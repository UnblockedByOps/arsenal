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
    TagNodeAssignment,
    )


@view_config(route_name='api_tag_node_assignments', request_method='GET', request_param='schema=true', renderer='json')
def api_tag_node_assignments_schema(request):
    """Schema document for the tag_node_assignments API"""

    tag_node_assignments = {
    }

    return tag_node_assignments


@view_config(route_name='api_tag_node_assignment_r', request_method='GET', renderer='json')
def api_tag_node_assignment_read_attrib(request):
    """Process read requests for the /api/tag_node_assignments/{id}/{resource} route."""

    return get_api_attribute(request, 'TagNodeAssignment')


@view_config(route_name='api_tag_node_assignment', request_method='GET', renderer='json')
def api_tag_node_assignment_read_id(request):
    """Process read requests for the /api/tag_node_assignments/{id} route."""

    return api_read_by_id(request, 'TagNodeAssignment')


@view_config(route_name='api_tag_node_assignments', request_method='GET', renderer='json')
def api_tag_node_assignment_read(request):
    """Process read requests for the /api/tag_node_assignments route."""

    return api_read_by_params(request, 'TagNodeAssignment')


@view_config(route_name='api_tag_node_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_tag_node_assignments_write(request):
    """Process write requests for the /api/tag_node_assignments route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        tag_id = payload['tag_id']
        node_id = payload['node_id']

        log.debug('Searching for tag_node_assignment tag_id={0}node_id={1}'.format(tag_id, node_id))
        try:
            tna = DBSession.query(TagNodeAssignment)
            tna = tna.filter(TagNodeAssignment.tag_id==tag_id)
            tna = tna.filter(TagNodeAssignment.node_id==node_id)
            tna = tna.one()
            log.info('tag_node_assignment already exists')
            return Response(content_type='application/json', status_int=409)
        except NoResultFound:
            try:
                log.info('Creating new tag_node_assignment tag_id={0},node_id={1}'.format(tag_id, node_id))
                utcnow = datetime.utcnow()

                ta = TagNodeAssignment(tag_id=tag_id,
                                       node_id=node_id,
                                       updated_by=au['user_id'],
                                       created=utcnow,
                                       updated=utcnow)

                DBSession.add(ta)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new tag_node_assignment tag_id={0},node_id={1},exception={2}'.format(tag_id, node_id, e))
                raise

    except Exception as e:
        log.error('Error writing to tag_node_assignments API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tag_node_assignment', permission='api_write', request_method='DELETE', renderer='json')
def api_tag_node_assignments_delete_id(request):
    """Process delete requests for the /api/tag_node_assignments/{id} route."""

    return api_delete_by_id(request, 'TagNodeAssignment')


@view_config(route_name='api_tag_node_assignments', permission='api_write', request_method='DELETE', renderer='json')
def api_tag_node_assignments_delete(request):
    """Process delete requests for the /api/tag_node_assignments route.
       Iterates over passed parameters."""

    return api_delete_by_params(request, 'TagNodeAssignment')


