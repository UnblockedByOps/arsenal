'''Arsenal API hypervisor_vm_assignments.'''
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
import logging
from datetime import datetime
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    )
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_404,
    api_500,
    )

LOG = logging.getLogger(__name__)


def guest_vms_to_hypervisor(guest_vms, hypervisor, action, user_id):
    '''Manage guest vm assignment/deassignments to a hypervisor. Takes a
    list if Node objects and assigns/deassigns them to/from the hypervisor.

    guest_vms: a list of Node objects to assign as guests to a hypervisor.
    hypervisor: A Node object to assign the guest_vms to.
    action: A string defining whether to assign  ('PUT') or de-assign
        ('DELETE') the guest vms to/from the hypervisor.
    user_id: A sting representing the user_id making this change.
    '''

    resp = {hypervisor.name: []}
    try:
        for guest_vm in guest_vms:
            resp[hypervisor.name].append(guest_vm.unique_id)

            utcnow = datetime.utcnow()

            if action == 'PUT':
                LOG.debug('HVMS: {0}'.format(hypervisor.guest_vms))
                if not guest_vm in hypervisor.guest_vms:
                    hypervisor.guest_vms.append(guest_vm)
                    audit = NodeAudit(object_id=hypervisor.id,
                                      field='guest_vm',
                                      old_value='assigned',
                                      new_value=guest_vm.name,
                                      updated_by=user_id,
                                      created=utcnow)
                    DBSession.add(audit)
            if action == 'DELETE':
                try:
                    hypervisor.guest_vms.remove(guest_vm)
                    audit = NodeAudit(object_id=hypervisor.id,
                                      field='guest_vm',
                                      old_value=guest_vm.name,
                                      new_value='deassigned',
                                      updated_by=user_id,
                                      created=utcnow)
                    DBSession.add(audit)
                except (ValueError, AttributeError):
                    try:
                        DBSession.remove(audit)
                    except  UnboundLocalError:
                        pass

        DBSession.add(hypervisor)
        DBSession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='hypervisor not found')

    except Exception as ex:
        msg = 'Error updating hypervisor: exception={0}'.format(ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return api_200(results=resp)

@view_config(route_name='api_hypervisor_vm_assignments', request_method='GET', request_param='schema=true', renderer='json')
def api_hypervisor_vm_assignments_schema(request):
    '''Schema document for the hypervisor_vm_assignments API.'''

    hva = {
    }

    return hva

@view_config(route_name='api_hypervisor_vm_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_hypervisor_vm_assignments_write(request):
    '''Process write requests for the /api/hypervisor_vm_assignments route.'''

    try:
        auth_user = get_authenticated_user(request)
        payload = request.json_body

        parent_node_id = int(payload['parent_node_id'])
        child_node_id = int(payload['child_node_id'])

        LOG.info('Checking for hypervisor_vm_assignment child_node_id={0}'.format(child_node_id))

        try:
            hva = DBSession.query(HypervisorVmAssignment)
            hva = hva.filter(HypervisorVmAssignment.child_node_id == child_node_id)
            hva = hva.one()
        except NoResultFound:
            try:
                LOG.info('Creating new hypervisor_vm_assignment parent_node_id={0},'
                         'child_node_id={1}'.format(parent_node_id, child_node_id))
                utcnow = datetime.utcnow()

                hva = HypervisorVmAssignment(parent_node_id=parent_node_id,
                                             child_node_id=child_node_id,
                                             updated_by=auth_user['user_id'],
                                             created=utcnow,
                                             updated=utcnow)

                DBSession.add(hva)
                DBSession.flush()
            except Exception as ex:
                LOG.error('Error creating new hypervisor_vm_assignment parent_node_id={0},'
                          'child_node_id={1},exception={2}'.format(parent_node_id,
                                                                   child_node_id,
                                                                   ex))
                raise
        else:
            try:
                LOG.info('Updating hypervisor_vm_assignment parent_node_id={0},'
                         'child_node_id={1}'.format(parent_node_id, child_node_id))

                hva.parent_node_id = parent_node_id
                hva.child_node_id = child_node_id
                hva.updated_by = auth_user['user_id']

                DBSession.flush()
            except Exception as ex:
                LOG.error('Error updating hypervisor_vm_assignment'
                          'parent_node_id={0},child_node_id={1},'
                          'exception={2}'.format(parent_node_id, child_node_id, ex))
                raise

    except Exception as ex:
        LOG.error('Error writing to hypervisor_vm_assignment API={0},'
                  'exception={1}'.format(request.url, ex))
        return Response(json={'error': str(ex)}, content_type='application/json', status_int=500)
