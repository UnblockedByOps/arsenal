'''Arsenal API bulk vm_assignments.'''
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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    enforce_api_change_limit,
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )

LOG = logging.getLogger(__name__)

def remove_guest_vms(dbsession, node_ids, user):
    '''Remove all guest_vms from a list of node_ids.'''

    resp = {'nodes': []}
    try:
        for node_id in node_ids:

            node = find_node_by_id(dbsession, node_id)
            LOG.debug('Removing all guest_vms from node: %s '
                      'guest_vms: %s', node.name, [gvm.name for gvm in node.guest_vms])
            resp['nodes'].append(node.name)
            utcnow = datetime.utcnow()

            LOG.debug('guest_vm objects: %s', node.guest_vms)
            for guest_vm in list(node.guest_vms):
                LOG.debug('Removing guest_vm : %s', guest_vm.name)
                try:
                    audit_hv = NodeAudit(object_id=node.id,
                                         field='guest_vm',
                                         old_value=guest_vm.name,
                                         new_value='deassigned',
                                         updated_by=user['name'],
                                         created=utcnow)
                    audit_guest = NodeAudit(object_id=guest_vm.id,
                                            field='hypervisor',
                                            old_value=node.name,
                                            new_value='deassigned',
                                            updated_by=user['name'],
                                            created=utcnow)
                    dbsession.add(audit_hv)
                    dbsession.add(audit_guest)

                    LOG.debug('Trying to remove guest_vm: %s from '
                              'node: %s', guest_vm.name, node.name)
                    node.guest_vms.remove(guest_vm)
                    LOG.debug('Successfully removed guest_vm: %s from '
                              'node: %s', guest_vm.name, node.name)
                except (ValueError, AttributeError) as ex:
                    LOG.debug('Died removing node_group: %s', ex)
                    dbsession.remove(audit_hv)
                    dbsession.remove(audit_guest)

            LOG.debug('Final guest_vms: %s', [gvm.name for gvm in node.guest_vms])
            dbsession.add(node)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node not found')
    except MultipleResultsFound:
        msg = 'Bad request: node_id is not unique: {0}'.format(node_id)
        return api_400(msg=msg)
    except Exception as ex:
        LOG.error('Error removing all guest_vms from node. exception: %s', ex)
        return api_500()

    return resp

@view_config(route_name='api_b_guest_vms_deassign', permission='api_write', request_method='DELETE', renderer='json', require_csrf=False)
def api_b_guest_vms_deassign(request):
    '''Process delete requests for the /api/bulk/guest_vms/deassign route.
    Takes a list of nodes and deassigns all guest_vms from them.'''

    try:
        payload = request.json_body
        node_ids = payload['node_ids']
        user = request.identity

        item_count = len(node_ids)
        denied = enforce_api_change_limit(request, item_count)
        if denied:
            return api_400(msg=denied)

        LOG.debug('Updating %s', request.url)

        try:
            resp = remove_guest_vms(request.dbsession, node_ids, user)
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(payload)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error removing all guest_vms from '
                      'node: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))

        return api_200(results=resp)

    except Exception as ex:
        LOG.error('Error updating guest_vms: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))
