'''Arsenal API nodes.'''
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
import json
import operator
from datetime import datetime
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from arsenalweb.models.nodes import (
    Node,
    NodeAudit,
    )
from arsenalweb.models.node_groups import (
    NodeGroup,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    )
from arsenalweb.views.api.data_centers import (
    find_data_center_by_name,
    create_data_center,
    )
from arsenalweb.views.api.hardware_profiles import (
    get_hardware_profile,
    create_hardware_profile,
    )
from arsenalweb.views.api.ip_addresses import (
    find_ip_addr_by_addr,
    create_ip_addr,
    )
from arsenalweb.views.api.operating_systems import (
    get_operating_system,
    create_operating_system,
    )
from arsenalweb.views.api.physical_devices import (
    update_physical_device,
    find_physical_device_by_serial,
    )
from arsenalweb.views.api.ec2_instances import (
    create_ec2_instance,
    find_ec2_instance_by_id,
    update_ec2_instance,
    )
from arsenalweb.views.api.network_interfaces import (
    find_net_if_by_unique_id,
    create_net_if,
    update_net_if,
    net_ifs_to_node,
    )
from arsenalweb.views.api.hypervisor_vm_assignments import (
    guest_vms_to_hypervisor,
    )
from arsenalweb.models.statuses import (
    Status,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_status_by_name(dbsession, status_name):
    '''Find a status by name.'''

    status = dbsession.query(Status)
    status = status.filter(Status.name == status_name)

    return status.one()

def find_node_by_name(dbsession, node_name):
    '''Find a node by name.'''

    node = dbsession.query(Node)
    node = node.filter(Node.name == node_name)

    return node.one()

def find_node_by_id(dbsession, node_id):
    '''Find a node by id.'''

    LOG.debug('START find_node_by_id()')
    node = dbsession.query(Node)
    node = node.filter(Node.id == node_id)

    one_node = node.one()
    LOG.debug('RETURN find_node_by_id()')
    return one_node

def find_node_by_unique_id(dbsession, unique_id):
    '''Find a node by it's unique_id.'''

    LOG.debug('START find_node_by_unique_id()')
    LOG.debug('Searching for node unique_id: %s', unique_id)
    node = dbsession.query(Node)
    node = node.filter(Node.unique_id == unique_id)

    one_node = node.one()
    LOG.debug('RETURN find_node_by_unique_id()')
    return one_node

def node_groups_to_nodes(dbsession, node, node_groups, action, auth_user):
    '''Manage node group assignment/deassignments. Takes a list of node_group
       names and assigns/deassigns them to/from the node.'''

    resp = {node.name: []}
    try:
        for node_group_name in node_groups:
            LOG.debug('node_group_name: %s', node_group_name)
            try:
                node_group = dbsession.query(NodeGroup)
                node_group = node_group.filter(NodeGroup.name == node_group_name)
                node_group = node_group.one()
            except Exception as ex:
                LOG.debug('Error querying DB: %s', ex)
                raise

            resp[node.name].append(node_group.name)

            utcnow = datetime.utcnow()

            if action == 'PUT':
                node.node_groups.append(node_group)
                audit = NodeAudit(object_id=node.id,
                                  field='node_group',
                                  old_value='created',
                                  new_value=node_group.name,
                                  updated_by=auth_user['user_id'],
                                  created=utcnow)
                dbsession.add(audit)
            if action == 'DELETE':
                try:
                    audit = NodeAudit(object_id=node.id,
                                      field='node_group',
                                      old_value=node_group.name,
                                      new_value='deleted',
                                      updated_by=auth_user['user_id'],
                                      created=utcnow)
                    dbsession.add(audit)
                    node.node_groups.remove(node_group)
                except (ValueError, AttributeError):
                    dbsession.remove(audit)

        dbsession.add(node)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node_group not found')

    except MultipleResultsFound:
        msg = 'Bad request: node group is not unique: {0}'.format(node_group)
        return api_400(msg=msg)
    except Exception as ex:
        LOG.error('Error updating node_group: exception: %s', ex)
        return api_500()

    return api_200(results=resp)

def process_network_interfaces(dbsession, network_interfaces, user):
    '''Process all network interfaces of a node during register.'''

    try:
        net_if_list = []
        LOG.debug('network interfaces: %s', json.dumps(network_interfaces,
                                                       indent=4,
                                                       sort_keys=True))
        for interface in network_interfaces:
            LOG.debug('Working on interface: %s', interface)
            ip_addr = None
            try:
                my_ip = interface['ip_address']
                if my_ip:
                    ip_addr = find_ip_addr_by_addr(dbsession, my_ip)
                    LOG.debug('IP Address found...')
                    # There's nothing to update. if we ever do have something, it will go here.
                else:
                    LOG.debug('This interface does not have an IP Address')
            except NoResultFound:
                LOG.debug('IP Address not found found, creating...')
                ip_addr = create_ip_addr(dbsession, ip_address=my_ip, updated_by=user)
            # This interface doesn't have an IP key passed.
            except KeyError:
                pass

            try:
                net_if = find_net_if_by_unique_id(dbsession, interface['unique_id'])
                LOG.debug('Interface found, updating...')
                if ip_addr:
                    interface['ip_address_id'] = ip_addr.id
                try:
                    # Remove this key if present, since update_net_if() doesn't
                    # have an ip_address kwarg.
                    del interface['ip_address']
                except KeyError:
                    pass
                updated_net_if = update_net_if(net_if, updated_by=user,
                                               **interface)
                net_if_list.append(updated_net_if)
            except NoResultFound:
                LOG.debug('Interface not found found, creating...')
                if ip_addr:
                    interface['ip_address_id'] = ip_addr.id
                try:
                    # Remove this key if present, since create_net_if() doesn't
                    # have an ip_address kwarg.
                    del interface['ip_address']
                except KeyError:
                    pass
                net_if = create_net_if(updated_by=user,
                                       **interface)
                net_if_list.append(net_if)

        return net_if_list

    except Exception as ex:
        LOG.error('Unable to determine network_interface! exception: %s', repr(ex))
        raise

def process_hardware_profile(dbsession, payload, user):
    '''Find the hardware_profile or create if it doesn't exist. Returns hardware_profile_id'''

    try:

        name = payload['hardware_profile']['name'].rstrip()
        manufacturer = payload['hardware_profile']['manufacturer'].rstrip()
        model = payload['hardware_profile']['model'].rstrip()

        hardware_profile = get_hardware_profile(dbsession, name)

        if not hardware_profile:
            hardware_profile = create_hardware_profile(dbsession,
                                                       name,
                                                       manufacturer,
                                                       model,
                                                       user)

        LOG.debug('hardware_profile is: %s', hardware_profile.__dict__)
        return hardware_profile

    except Exception as ex:
        LOG.error('Unable to determine hardware_profile manufacturer: %s model: %s '
                  'exception: %s', manufacturer, model, ex)
        raise

def process_operating_system(dbsession, payload, user):
    '''Find the operating_system or create if it doesn't exist. Returns operating_system_id.'''

    try:
        name = payload['operating_system']['name'].rstrip()
        variant = payload['operating_system']['variant'].rstrip()
        version_number = payload['operating_system']['version_number'].rstrip()
        architecture = payload['operating_system']['architecture'].rstrip()
        description = payload['operating_system']['description'].rstrip()

        operating_system = get_operating_system(dbsession, name)

        if not operating_system:
            operating_system = create_operating_system(dbsession,
                                                       name,
                                                       variant,
                                                       version_number,
                                                       architecture,
                                                       description,
                                                       user)

        LOG.debug('operating_system is: %s', operating_system.__dict__)
        return operating_system

    except Exception as ex:
        LOG.error('Unable to determine operating_system name: %s variant: %s '
                  'version_number: %s architecture: %s description: %s '
                  'exception: %s', name,
                                   variant,
                                   version_number,
                                   architecture,
                                   description,
                                   ex)
        raise

def process_ec2(dbsession, payload, user):
    '''If present in the payload, Get the ec2_object or create if it doesn't
    exist. Returns ec2.id, or None if not present in the payload.'''

    try:
        account_id = payload['ec2']['account_id'].rstrip()
        ami_id = payload['ec2']['ami_id'].rstrip()
        hostname = payload['ec2']['hostname'].rstrip()
        instance_id = payload['ec2']['instance_id'].rstrip()
        instance_type = payload['ec2']['instance_type'].rstrip()
        availability_zone = payload['ec2']['availability_zone'].rstrip()
        profile = payload['ec2']['profile'].rstrip()
        reservation_id = payload['ec2']['reservation_id'].rstrip()
        security_groups = payload['ec2']['security_groups'].rstrip()

        ec2 = find_ec2_instance_by_id(dbsession, instance_id)
        ec2 = update_ec2_instance(dbsession,
                                  ec2,
                                  account_id=account_id,
                                  ami_id=ami_id,
                                  hostname=hostname,
                                  instance_id=instance_id,
                                  instance_type=instance_type,
                                  availability_zone=availability_zone,
                                  profile=profile,
                                  reservation_id=reservation_id,
                                  security_groups=security_groups,
                                  updated_by=user)

    except NoResultFound:
        ec2 = create_ec2_instance(dbsession, account_id=account_id,
                                  ami_id=ami_id,
                                  hostname=hostname,
                                  instance_id=instance_id,
                                  instance_type=instance_type,
                                  availability_zone=availability_zone,
                                  profile=profile,
                                  reservation_id=reservation_id,
                                  security_groups=security_groups,
                                  updated_by=user)

    except (TypeError, KeyError, AttributeError):
        LOG.debug('ec2_instance data not present in payload.')
        return None

    except Exception as ex:
        LOG.error('Unable to determine ec2_instance! exception: %s', repr(ex))
        raise

    LOG.debug('ec2_instance is: %s', ec2.__dict__)
    return ec2

def process_data_center(dbsession, payload, user):
    '''Find the data_center or create if it doesn't exist. Returns data_center.id'''

    try:
        name = payload['data_center']['name'].rstrip()

        data_center = find_data_center_by_name(dbsession, name)

    except NoResultFound:
        LOG.debug('data_center data not found, creating...')
        resp = create_data_center(dbsession, name=name, updated_by=user)
        data_center = resp['results'][0]

    except (TypeError, KeyError):
        LOG.debug('data_center data not present in payload.')
        return None

    except Exception as ex:
        LOG.error('Unable to determine datacenter name: %s '
                  'exception: %s', name, repr(ex))
        raise

    LOG.debug('data_center is: %s', data_center.__dict__)
    return data_center

def manage_guest_vm_assignments(dbsession, guest_vms, hypervisor, user_id):
    '''Manage the assigning and deassinging of guests during a node
    registration.'''

    all_guests = []
    for gvm in guest_vms:
        try:
            LOG.debug('Attempting to assign vm: %s', gvm['name'])
            all_guests.append(find_node_by_unique_id(dbsession, gvm['unique_id']))
        except NoResultFound:
            LOG.debug('vm not found: %s', gvm['name'])
    LOG.debug('ALL GUESTS: %s', all_guests)
    guest_vms_to_hypervisor(dbsession, all_guests, hypervisor, 'PUT', user_id)
    # Deassign guest_vms the node no longer has.
    deassign_guest_vms = [x for x in hypervisor.guest_vms if x not in all_guests]
    LOG.debug('DEASSIGN GUESTS: %s', deassign_guest_vms)
    guest_vms_to_hypervisor(dbsession, deassign_guest_vms, hypervisor, 'DELETE', user_id)

def create_node(dbsession, **kwargs):
    '''Create a new node.'''

    user_id = kwargs['user_id']
    unique_id = kwargs['unique_id']
    name = kwargs['name']
    hardware_profile_id = kwargs['hardware_profile_id']
    operating_system_id = kwargs['operating_system_id']
    data_center_id = kwargs['data_center_id']
    ec2_id = kwargs['ec2_id']
    serial_number = kwargs['serial_number']
    os_memory = kwargs['os_memory']
    processor_count = kwargs['processor_count']
    uptime = kwargs['uptime']
    user_id = kwargs['user_id']
    net_if_list = kwargs['net_if_list']

    try:
        LOG.info('Creating new node name: %s unique_id: %s', name, unique_id)
        utcnow = datetime.utcnow()

        node = Node(unique_id=unique_id,
                    name=name,
                    hardware_profile_id=hardware_profile_id,
                    operating_system_id=operating_system_id,
                    data_center_id=data_center_id,
                    status_id=2,
                    ec2_id=ec2_id,
                    serial_number=serial_number,
                    os_memory=os_memory,
                    processor_count=processor_count,
                    uptime=uptime,
                    updated_by=user_id,
                    last_registered=utcnow,
                    created=utcnow,
                    updated=utcnow)

        dbsession.add(node)
        dbsession.flush()

        audit = NodeAudit(object_id=node.id,
                          field='unique_id',
                          old_value='created',
                          new_value=node.unique_id,
                          updated_by=user_id,
                          created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        net_ifs_to_node(dbsession, net_if_list, node, 'PUT', user_id)

        # Ensure that brand new nodes update the status of the physical device
        # to allocated.
        try:
            my_physical_device = find_physical_device_by_serial(dbsession, serial_number)
            update_physical_device(dbsession, my_physical_device,
                                   status_id=10,
                                   updated_by=user_id)
        except NoResultFound:
            pass

    except Exception as ex:
        LOG.error('Error creating new node name: %s unique_id: %s '
                  'exception: %s', name, unique_id, repr(ex))
        raise

    return node

def update_node(dbsession, node, settings, **kwargs):
    '''Update an existing node.'''

    user_id = kwargs['user_id']
    unique_id = kwargs['unique_id']
    name = kwargs['name']
    hardware_profile_id = kwargs['hardware_profile_id']
    hardware_profile_name = kwargs['hardware_profile_name']
    operating_system_id = kwargs['operating_system_id']
    operating_system_name = kwargs['operating_system_name']
    data_center_id = kwargs['data_center_id']
    data_center_name = kwargs['data_center_name']
    ec2_id = kwargs['ec2_id']
    ec2_instance_id = kwargs['ec2_instance_id']
    serial_number = kwargs['serial_number']
    os_memory = kwargs['os_memory']
    processor_count = kwargs['processor_count']
    uptime = kwargs['uptime']
    user_id = kwargs['user_id']
    net_if_list = kwargs['net_if_list']

    # Remap for audit entries so we can have values instead of IDs.
    audit_remap = {
        'hardware_profile_id': 'hardware_profile_name',
        'operating_system_id': 'operating_system_name',
        'data_center_id': 'data_center_name',
        'ec2_id': 'ec2_instance_id',
    }

    try:
        LOG.info('Updating node: %s', unique_id)

        utcnow = datetime.utcnow()

        for attribute in ['name',
                          'hardware_profile_id',
                          'operating_system_id',
                          'data_center_id',
                          'ec2_id',
                          'serial_number',
                          'os_memory',
                          'processor_count',
                          'uptime']:
            if getattr(node, attribute) != locals()[attribute]:
                LOG.debug('Updating node %s: %s', attribute, locals()[attribute])
                # We don't want audit entries for uptime
                if attribute != 'uptime':
                    if attribute.endswith('_id') and attribute != 'ec2_id':
                        obj_name = '{0}.name'.format(attribute[:-3])
                        LOG.info('Updating object name: %s', obj_name)
                        try:
                            old_value = operator.attrgetter(obj_name)(node)
                        except AttributeError:
                            old_value = 'None'
                    elif attribute == 'ec2_id':
                        old_value = node.ec2.instance_id
                    else:
                        # This will not set 'None' to a string.
                        old_value = getattr(node, attribute, 'None')

                    if not old_value:
                        old_value = 'None'

                    try:
                        update_field = audit_remap[attribute]
                        update_value = locals()[update_field]
                    except KeyError:
                        update_field = attribute
                        update_value = locals()[attribute]

                    audit = NodeAudit(object_id=node.id,
                                      field=update_field,
                                      old_value=old_value,
                                      new_value=update_value,
                                      updated_by=user_id,
                                      created=utcnow)
                    dbsession.add(audit)

        node.name = name
        node.hardware_profile_id = hardware_profile_id
        node.operating_system_id = operating_system_id
        node.data_center_id = data_center_id
        node.ec2_id = ec2_id
        node.serial_number = serial_number
        node.os_memory = os_memory
        node.processor_count = processor_count
        node.uptime = uptime
        node.updated_by = user_id
        node.last_registered = utcnow

        net_ifs_to_node(dbsession, net_if_list, node, 'PUT', user_id)
        # Deassign network_interfaces the node no longer has.
        deassign_net_ifs = [x for x in node.network_interfaces if x not in net_if_list]
        net_ifs_to_node(dbsession, deassign_net_ifs, node, 'DELETE', user_id)

        # Manage guest_vm assignemnts
        try:
            manage_guest_vm_assignments(dbsession, kwargs['guest_vms'], node, user_id)
        except KeyError:
            pass

        try:
            current_hwp = node.physical_device.hardware_profile.id
            if current_hwp != hardware_profile_id:
                LOG.debug('Updating physical_device.hardware_profile_id from: '
                          '%s to: %s', current_hwp, hardware_profile_id)
                update_physical_device(dbsession,
                                       node.physical_device,
                                       hardware_profile_id=hardware_profile_id,
                                       updated_by=user_id)
            else:
                LOG.debug('physical_device.hardware_profile_id matches what '
                          'is being reported by node registration.')

            pd_status = getattr(settings, 'arsenal.node_hw_map.{0}'.format(node.status.name))
            final_status = find_status_by_name(dbsession, pd_status)
            final_status_id = final_status.id

            if node.physical_device.status_id != final_status_id:

                LOG.debug('Updating physical_device.status_id from: '
                          '%s to: %s', node.physical_device.status_id,
                                       final_status_id)
                update_physical_device(dbsession,
                                       node.physical_device,
                                       status_id=final_status_id,
                                       updated_by=user_id)
            else:
                LOG.debug('physical_device.status_id matches the '
                          'nodes current status per the map.')
        except AttributeError:
            LOG.debug('No physical_device for node, not checking '
                      'physical_device.hardware_profile_id for update.')

        dbsession.flush()
    except Exception as ex:
        LOG.error('Error updating node name: %s unique_id: %s '
                  'exception: %s', name, unique_id, repr(ex))
        raise

    return node

def process_registration_payload(dbsession, payload, user_id):
    '''Process the payload of a node registration and return a dictionary for
    updating or creating a node.'''

    LOG.debug('Processing registration payload...')

    try:
        processed = {}
        processed['user_id'] = user_id
        processed['unique_id'] = payload['unique_id'].lower().rstrip()
        processed['name'] = payload['name'].rstrip()
        processed['serial_number'] = payload['serial_number'].rstrip()
        try:
            processed['os_memory'] = payload['os_memory'].rstrip()
        except (KeyError, AttributeError):
            processed['os_memory'] = None
        processed['processor_count'] = int(payload['processor_count'])
        processed['uptime'] = payload['uptime'].rstrip()

        hardware_profile = process_hardware_profile(dbsession, payload, user_id)
        processed['hardware_profile_id'] = hardware_profile.id
        processed['hardware_profile_name'] = hardware_profile.name

        operating_system = process_operating_system(dbsession, payload, user_id)
        processed['operating_system_id'] = operating_system.id
        processed['operating_system_name'] = operating_system.name

        data_center = process_data_center(dbsession, payload, user_id)
        try:
            processed['data_center_id'] = data_center.id
            processed['data_center_name'] = data_center.name
        except AttributeError:
            processed['data_center_id'] = None
            processed['data_center_name'] = None

        ec2 = process_ec2(dbsession, payload, user_id)
        try:
            processed['ec2_id'] = ec2.id
            processed['ec2_instance_id'] = ec2.instance_id
        except AttributeError:
            processed['ec2_id'] = None
            processed['ec2_instance_id'] = None
    except KeyError as ex:
        LOG.error('Required data missing from payload: %s', repr(ex))
        raise
    except (TypeError, ValueError) as ex:
        LOG.error('Incorrect data type for payload item: %s', repr(ex))
        raise
    except Exception as ex:
        LOG.error('Unhandled data problem for payload item: %s', repr(ex))
        raise
    try:
        processed['guest_vms'] = payload['guest_vms']
    except KeyError:
        pass

    # Every host should have at least one IP address and network interface.
    processed['net_if_list'] = process_network_interfaces(dbsession,
                                                          payload['network_interfaces'],
                                                          user_id)
    return processed

@view_config(route_name='api_nodes', request_method='GET', request_param='schema=true', renderer='json')
def api_node_schema(request):
    '''Schema document for nodes API'''

    LOG.debug('schema requested')

    node = {
    }

    return node

@view_config(route_name='api_node_r', permission='node_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_node_r', permission='node_write', request_method='PUT', renderer='json', require_csrf=False)
def api_node_write_attrib(request):
    '''Process write requests for the /api/nodes/{id}/{resource} route.'''

    try:
        resource = request.matchdict['resource']
        payload = request.json_body
        user = request.identity

        LOG.debug('Updating %s', request.url)
        LOG.debug('resource type: %s', resource)

        # First get the node, then figure out what to do to it.
        node = find_node_by_id(request.dbsession, request.matchdict['id'])
        LOG.debug('node is: %s', node)

        # List of resources allowed
        resources = [
            'node_groups',
        ]

        if resource in resources:
            try:
                actionable = payload[resource]
                if resource == 'node_groups':
                    resp = node_groups_to_nodes(request.dbsession,
                                                node,
                                                actionable,
                                                request.method,
                                                user)
            except KeyError:
                msg = 'Missing required parameter: {0}'.format(resource)
                return api_400(msg=msg)
            except Exception as ex:
                LOG.error('Error updating nodes: %s exception: %s', request.url, ex)
                return api_500(msg=str(ex))
        else:
            return api_501()

        return resp

    except Exception as ex:
        LOG.error('Error updating nodes: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))

@view_config(route_name='api_node', permission='node_write', request_method='PUT', renderer='json', require_csrf=False)
def api_node_write_id(request):
    '''Process write requests for the /api/nodes/{id} route.'''

    try:
        user = request.identity
        node_id = request.matchdict['id']
        payload = request.json_body

        params = ''
        for key, val in payload.items():
            params += '{0}={1},'.format(key, val)

        LOG.info('Updating node_id: %s params: %s', node_id,
                                                     params.rstrip(','))

        node = request.dbsession.query(Node)
        node = node.filter(Node.id == node_id)
        node = node.one()

        # FIXME: Do we want to limit anything here? Keys that don't exist will
        # be ignored, keys that can't be set with throw an error. Doesn't
        # feel right though to just accept what's put to the endpoint.
        for key, val in payload.items():
            try:
                setattr(node, key, val.rstrip())
            except AttributeError:
                setattr(node, key, int(val))

        node.updated_by = user['name']
        request.dbsession.flush()

    except Exception as ex:
        LOG.error('Error writing to nodes API: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))

    return node

@view_config(route_name='api_register', permission='api_register', request_method='PUT', renderer='json', require_csrf=False)
def api_node_register(request):
    '''Process registration requests for the /api/register route.'''

    try:
        LOG.info('Registering node')
        user = request.identity
        payload = request.json_body
        processed = process_registration_payload(request.dbsession, payload, user['name'])
        settings = request.registry.settings

        try:
            existing_node = find_node_by_unique_id(request.dbsession, processed['unique_id'])
            node = update_node(request.dbsession, existing_node, settings, **processed)
        except NoResultFound:
            node = create_node(request.dbsession, **processed)

        return api_200(results=node)

    except Exception as ex:
        msg = 'Error registering new node: {0} API: {1} exception: ' \
              '{2}'.format(processed['name'], request.url, repr(ex))
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_nodes', permission='node_write', request_method='PUT', renderer='json', require_csrf=False)
def api_node_write(request):
    '''Process write requests for the /api/nodes route.'''

    try:
        user = request.identity
        payload = request.json_body

        # Manually created node via the client.
        try:
            node_name = payload['name'].rstrip()
            unique_id = payload['unique_id'].lower().rstrip()
            status_id = int(payload['status_id'])
            operating_system_id = int(payload['operating_system']['id'])
            hardware_profile_id = int(payload['hardware_profile']['id'])

            LOG.debug('Searching for node unique_id: %s', unique_id)
            node = request.dbsession.query(Node)
            node = node.filter(Node.unique_id == unique_id)
            node = node.one()

            LOG.info('Updating node name: %s unique_id: %s', node_name, unique_id)

            utcnow = datetime.utcnow()

            # FIXME: This should iterate over all updateable params, not be
            # hardcoded to name and status_id.
            if node.name != node_name:
                audit = NodeAudit(object_id=node.id,
                                  field='node_name',
                                  old_value=node.name,
                                  new_value=node_name,
                                  updated_by=user['name'],
                                  created=utcnow)
                request.dbsession.add(audit)
                node.name = node_name

            if node.status_id != status_id:
                audit_status = NodeAudit(object_id=node.id,
                                         field='status_id',
                                         old_value=node.status_id,
                                         new_value=status_id,
                                         updated_by=user['name'],
                                         created=utcnow)
                request.dbsession.add(audit_status)
                node.status_id = status_id

            node.updated_by = user['name']
            request.dbsession.flush()

        except NoResultFound:
            try:

                LOG.info('Manually creating new node name: %s unique_id: %s', node_name,
                                                                              unique_id)
                utcnow = datetime.utcnow()

                node = Node(name=node_name,
                            unique_id=unique_id,
                            status_id=status_id,
                            operating_system_id=operating_system_id,
                            hardware_profile_id=hardware_profile_id,
                            updated_by=user['name'],
                            last_registered=utcnow,
                            created=utcnow,
                            updated=utcnow)


                request.dbsession.add(node)
                request.dbsession.flush()

                audit = NodeAudit(object_id=node.id,
                                  field='unique_id',
                                  old_value='created',
                                  new_value=node.unique_id,
                                  updated_by=user['name'],
                                  created=utcnow)
                request.dbsession.add(audit)
                request.dbsession.flush()

            except Exception as ex:
                LOG.error('Error creating new node name: %s unique_id: %s status_id: %s '
                          'exception: %s', node_name, unique_id, status_id, ex)
                raise

        return api_200(results=node)

    except Exception as ex:
        LOG.error('Error writing to nodes API: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))
