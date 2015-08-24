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
    HypervisorVmAssignment,
    )


@view_config(route_name='api_hypervisor_vm_assignments', request_method='GET', request_param='schema=true', renderer='json')
def api_hypervisor_vm_assignments_schema(request):
    """Schema document for the hypervisor_vm_assignments API."""

    hva = {
    }

    return hva


@view_config(route_name='api_hypervisor_vm_assignment_r', request_method='GET', renderer='json')
def api_hypervisor_vm_assignment_read_attrib(request):
    """Process read requests for the /api/hypervisor_vm_assignments/{id}/{resource} route."""

    return get_api_attribute(request, 'HypervisorVmAssignment')


@view_config(route_name='api_hypervisor_vm_assignment', request_method='GET', renderer='json')
def api_hypervisor_vm_assignment_read_id(request):
    """Process read requests for the /api/hypervisor_vm_assignments/{id} route."""

    return api_read_by_id(request, 'HypervisorVmAssignment')


@view_config(route_name='api_hypervisor_vm_assignments', request_method='GET', renderer='json')
def api_hypervisor_vm_assignment_read(request):
    """Process read requests for the /api/hypervisor_vm_assignments route."""

    return api_read_by_params(request, 'HypervisorVmAssignment')


@view_config(route_name='api_hypervisor_vm_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_hypervisor_vm_assignments_write(request):
    """Process write requests for the /api/hypervisor_vm_assignments route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        parent_node_id = payload['parent_node_id']
        child_node_id = payload['child_node_id']

        log.info('Checking for hypervisor_vm_assignment child_node_id={0}'.format(child_node_id))

        try:
            hva = DBSession.query(HypervisorVmAssignment)
            hva = hva.filter(HypervisorVmAssignment.child_node_id==child_node_id)
            hva = hva.one()
        except NoResultFound:
            try:
                log.info('Creating new hypervisor_vm_assignment parent_node_id={0},child_node_id={1}'.format(parent_node_id, child_node_id))
                utcnow = datetime.utcnow()

                hva = HypervisorVmAssignment(parent_node_id=parent_node_id,
                                             child_node_id=child_node_id,
                                             updated_by=au['user_id'],
                                             created=utcnow,
                                             updated=utcnow)

                DBSession.add(hva)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new hypervisor_vm_assignment parent_node_id={0},child_node_id={1},exception={2}'.format(parent_node_id, child_node_id, e))
                raise
        else:
            try:
                log.info('Updating hypervisor_vm_assignment parent_node_id={0},child_node_id={1}'.format(parent_node_id, child_node_id))

                hva.parent_node_id = parent_node_id
                hva.child_node_id = child_node_id
                hva.updated_by=au['user_id']

                DBSession.flush()
            except Exception as e:
                log.error('Error updating hypervisor_vm_assignment parent_node_id={0},child_node_id={1},exception={2}'.format(parent_node_id, child_node_id, e))
                raise

    except Exception as e:
        log.error('Error writing to hypervisor_vm_assignment API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_hypervisor_vm_assignment', permission='api_write', request_method='DELETE', renderer='json')
def api_hypervisor_vm_assignments_delete_id(request):
    """Process delete requests for the /api/hypervisor_vm_assignments/{id} route."""

    return api_delete_by_id(request, 'HypervisorVmAssignment')


@view_config(route_name='api_hypervisor_vm_assignments', permission='api_write', request_method='DELETE', renderer='json')
def api_hypervisor_vm_assignments_delete(request):
    """Process delete requests for the /api/hypervisor_vm_assignments route.
       Iterates over passed parameters."""

    return api_delete_by_params(request, 'HypervisorVmAssignment')
