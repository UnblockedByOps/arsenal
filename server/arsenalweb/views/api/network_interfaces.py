'''Arsenal API network_interfaces.'''
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
from arsenalweb.models.ip_addresses import (
    IpAddressAudit,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.models.network_interfaces import (
    NetworkInterface,
    NetworkInterfaceAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    collect_params,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_net_if_by_unique_id(dbsession, unique_id):
    '''Find a network_interface by unique_id. Return an object if found, raises
       an exception otherwise.'''

    unique_id = unique_id.lower()
    LOG.debug('Searching for network_interface.unique_id: %s', unique_id)
    net_if = dbsession.query(NetworkInterface)
    net_if = net_if.filter(NetworkInterface.unique_id == unique_id)

    return net_if.one()

def find_net_if_by_id(dbsession, net_if_id):
    '''Find a network_interface by id. Return an object if found, raises
       an exception otherwise.'''

    LOG.debug('Searching for network_interface.id: %s', net_if_id)
    net_if = dbsession.query(NetworkInterface)
    net_if = net_if.filter(NetworkInterface.id == net_if_id)

    return net_if.one()

def create_net_if(dbsession,
                  name=None,
                  unique_id=None,
                  updated_by=None,
                  ip_address_id=None,
                  bond_master=None,
                  mac_address=None,
                  port_description=None,
                  port_number=None,
                  port_switch=None,
                  port_vlan=None,
                  seen_mac_address=None,):
    '''Create a new network_interface.'''

    try:
        # Convert everything that is defined to a string.
        my_attribs = locals().copy()
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])
        # Guarantee unique_id is lowercase
        unique_id = unique_id.lower()
        # Guarantee ip_address_id is an int
        try:
            ip_address_id = int(ip_address_id)
        except TypeError:
            pass

        LOG.info('Creating new network_interface name: %s unique_id: %s '
                 'ip_address_id: %s updated_by: %s bond_master: %s mac_address: %s '
                 'port_description: %s port_number: %s port_switch: %s '
                 'port_vlan: %s seen_mac_address: %s', name,
                                                       unique_id,
                                                       ip_address_id,
                                                       updated_by,
                                                       bond_master,
                                                       mac_address,
                                                       port_description,
                                                       port_number,
                                                       port_switch,
                                                       port_vlan,
                                                       seen_mac_address)

        utcnow = datetime.utcnow()

        net_if = NetworkInterface(name=name,
                                  unique_id=unique_id,
                                  ip_address_id=ip_address_id,
                                  bond_master=bond_master,
                                  mac_address=mac_address,
                                  port_description=port_description,
                                  port_number=port_number,
                                  port_switch=port_switch,
                                  port_vlan=port_vlan,
                                  seen_mac_address=seen_mac_address,
                                  updated_by=updated_by,
                                  created=utcnow,
                                  updated=utcnow)

        dbsession.add(net_if)
        dbsession.flush()

        audit = NetworkInterfaceAudit(object_id=net_if.id,
                                      field='unique_id',
                                      old_value='created',
                                      new_value=net_if.unique_id,
                                      updated_by=updated_by,
                                      created=utcnow)
        dbsession.add(audit)

        if ip_address_id:
            LOG.debug('Creating audit entry for ip_address assignment '
                      'to network_interface...')
            ip_addr_audit = IpAddressAudit(object_id=ip_address_id,
                                           field='net_if_assignment',
                                           old_value='created',
                                           new_value=net_if.id,
                                           updated_by=updated_by,
                                           created=utcnow)

            dbsession.add(ip_addr_audit)

        dbsession.flush()

        return net_if

    except Exception as ex:
        msg = f'''Error creating new network_interface name: {name} unique_id: {unique_id}
ip_address_id: {ip_address_id} updated_by: {updated_by} bond_master: {bond_master}
mac_address: {mac_address} port_description: {port_description} port_number: {port_number}
port_switch: {port_switch} port_vlan: {port_vlan} seen_mac_address: {seen_mac_address}
exception: {ex}'''
        LOG.error(msg)
        return api_500(msg=msg)

def update_net_if(dbsession,
                  net_if,
                  name=None,
                  unique_id=None,
                  updated_by=None,
                  ip_address_id=None,
                  bond_master=None,
                  mac_address=None,
                  port_description=None,
                  port_number=None,
                  port_switch=None,
                  port_vlan=None,
                  seen_mac_address=None,):
    '''Update an existing network_interface.'''

    try:
        # Convert everything that is defined to a string.
        my_attribs = locals().copy()
        my_attribs.pop('dbsession')
        my_attribs.pop('net_if')
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])
        # Guarantee unique_id is lowercase
        my_attribs['unique_id'] = my_attribs['unique_id'].lower()
        # Guarantee ip_address_id is an int
        try:
            my_attribs['ip_address_id'] = int(my_attribs['ip_address_id'])
        except TypeError:
            pass

        LOG.info('Updating network_interface.unique_id: %s', my_attribs['unique_id'])

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'unique_id':
                LOG.debug('Skipping update to unique_id.')
                continue
            old_value = getattr(net_if, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating network_interface: %s attribute: '
                          '%s new_value: %s', my_attribs['unique_id'],
                                              attribute,
                                              new_value)
                net_if_audit = NetworkInterfaceAudit(object_id=net_if.id,
                                                     field=attribute,
                                                     old_value=old_value,
                                                     new_value=new_value,
                                                     updated_by=updated_by,
                                                     created=utcnow)
                dbsession.add(net_if_audit)
                setattr(net_if, attribute, new_value)

                if attribute == 'ip_address_id':
                    LOG.debug('Creating audit entry for ip_address assignment '
                              'to network_interface...')
                    ip_addr_audit = IpAddressAudit(object_id=my_attribs['ip_address_id'],
                                                   field='net_if_assignment',
                                                   old_value=old_value,
                                                   new_value=new_value,
                                                   updated_by=updated_by,
                                                   created=utcnow)

                    dbsession.add(ip_addr_audit)

        dbsession.flush()

        return net_if

    except Exception as ex:
        msg = f'''Error creating new network_interface name: {name} unique_id:
{my_attribs['unique_id']} ip_address_id: {ip_address_id} updated_by: {updated_by}
bond_master: {bond_master} mac_address: {mac_address} port_description:
{port_description} port_number: {port_number} port_switch: {port_switch}
port_vlan: {port_vlan} seen_mac_address: {seen_mac_address} exception: {ex}'''
        LOG.error(msg)
        raise

def net_ifs_to_node(dbsession, network_interfaces, node, action, user_id):
    '''Manage network_interface assignment/deassignments to a node. Takes a
    list if network_interface objects and assigns/deassigns them to/from the node.

    network_interfaces: a list of NetworkInterface objects to assign to a node.
    node: A Node object to assign the network_interfaces to.
    action: A string defining whether to assign  ('PUT') or de-assign
        ('DELETE') the network interfaces to/from the node.
    user_id: A sting representing the user_id making this change.
    '''

    resp = {node.name: []}
    try:
        for net_if in network_interfaces:
            resp[node.name].append(net_if.unique_id)

            utcnow = datetime.utcnow()

            if action == 'PUT':
                if not net_if in node.network_interfaces:
                    node.network_interfaces.append(net_if)
                    audit = NodeAudit(object_id=node.id,
                                      field='network_interface_id',
                                      old_value='assigned',
                                      new_value=net_if.id,
                                      updated_by=user_id,
                                      created=utcnow)
                    dbsession.add(audit)
            if action == 'DELETE':
                try:
                    node.network_interfaces.remove(net_if)
                    audit = NodeAudit(object_id=node.id,
                                      field='network_interface_id',
                                      old_value=net_if.id,
                                      new_value='deassigned',
                                      updated_by=user_id,
                                      created=utcnow)
                    dbsession.add(audit)
                except (ValueError, AttributeError):
                    try:
                        dbsession.remove(audit)
                    except  UnboundLocalError:
                        pass

        dbsession.add(node)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node not found')

    except Exception as ex:
        msg = 'Error updating node: exception={0}'.format(ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return api_200(results=resp)

# Routes
@view_config(route_name='api_network_interfaces', request_method='GET', request_param='schema=true', renderer='json')
def api_node_groups_schema(request):
    '''Schema document for the network_interfaces API.'''

    network_interfaces = {
    }

    return network_interfaces

# FIXME: Need to create the perms if we start allowing manual updates
@view_config(route_name='api_network_interfaces', permission='network_interface_write', request_method='PUT', renderer='json', require_csrf=False)
def api_network_interfaces_write(request):
    '''Process write requests for /api/network_interfaces route.'''

    try:
        req_params = [
            'name',
            'unique_id',
        ]
        opt_params = [
            'ip_address',
            'bond_master',
            'port_description',
            'port_number',
            'port_switch',
            'port_vlan',
        ]
        params = collect_params(request, req_params, opt_params)
        params['unique_id'] = params['unique_id'].lower()

        try:
            net_if = find_net_if_by_unique_id(request.dbsession, params['unique_id'])
            update_net_if(request.dbsession, net_if, **params)
        except NoResultFound:
            net_if = create_net_if(**params)

        return net_if

    except Exception as ex:
        msg = 'Error writing to network_interfaces API={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

# FIXME: Need to create the perms if we start allowing manual add/delete
@view_config(route_name='api_network_interface_r', permission='network_interface_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_network_interface_r', permission='network_interface_write', request_method='PUT', renderer='json', require_csrf=False)
def api_network_interface_write_attrib(request):
    '''Process write requests for the /api/network_interfaces/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body

    LOG.debug('Updating %s', request.url)

    # First get the network_interfaces, then figure out what to do to it.
    net_if = find_net_if_by_id(request.dbsession, request.matchdict['id'])
    LOG.debug('net_if is: %s', net_if)

    # List of resources allowed
    resources = [
        'undef',
    ]

    if resource in resources:
        try:
            actionable = payload[resource]
            if resource == 'undef':
                LOG.warning('Not allowed.')
                resp = []
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating network_interfaces: %s '
                      'exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return resp
