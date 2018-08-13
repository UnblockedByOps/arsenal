'''Arsenal API IpAddresses.'''
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
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.ip_addresses import (
    IpAddress,
    IpAddressAudit,
    )
from arsenalweb.models.network_interfaces import (
    NetworkInterfaceAudit,
    )
from arsenalweb.views import (
    get_authenticated_user,
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
def find_ip_addr_by_addr(ip_address):
    '''Find an ip_address by ip_address. Return an object if found, raises
    an exception otherwise.'''

    LOG.debug('Searching for ip_address.ip_address: '
              '{0}'.format(ip_address))
    ip_addr = DBSession.query(IpAddress)
    ip_addr = ip_addr.filter(IpAddress.ip_address == ip_address)

    return ip_addr.one()

def find_ip_addr_by_id(ip_addr_id):
    '''Find a ip_address by id. Return an object if found, raises an exception
    otherwise.'''

    LOG.debug('Searching for ip_address.id: {0}'.format(ip_addr_id))
    ip_addr = DBSession.query(IpAddress)
    ip_addr = ip_addr.filter(IpAddress.id == ip_addr_id)

    return ip_addr.one()

def create_ip_addr(ip_address=None, updated_by=None):
    '''Create a new ip_address.'''

    try:
        LOG.info('Creating new ip_address: {0}'.format(ip_address))

        utcnow = datetime.utcnow()
        ip_address = IpAddress(ip_address=ip_address,
                               updated_by=updated_by,
                               created=utcnow,
                               updated=utcnow)

        DBSession.add(ip_address)
        DBSession.flush()

        ip_address_audit = IpAddressAudit(object_id=ip_address.id,
                                          field='ip_address',
                                          old_value='created',
                                          new_value=ip_address.ip_address,
                                          updated_by=updated_by,
                                          created=utcnow)
        DBSession.add(ip_address_audit)
        DBSession.flush()

    except Exception as ex:
        msg = 'Error creating ip_address: {0} exception: {2}'.format(ip_address, ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return ip_address

def update_ip_addr(ip_address=None, user_id=None):
    '''Update an ip_address. We are not allowing this for now, just a
    placeholder. If we decide to add feilds we want to allow in the future,
    copy the implementation from netowrk_interfaces.'''
    return None

def ip_address_to_net_if(ip_address, net_if, user):
    '''Assign an ip_address to a network_interface.

       ip_address = An IpAddress object.
       net_if = A NetworkInterface object.
       user = A string representing the user_id making the change.
       '''

    LOG.debug('START ip_address_to_net_if()')
    resp = {ip_address.ip_address: []}
    try:

        utcnow = datetime.utcnow()

        with DBSession.no_autoflush:
            resp[ip_address.ip_address].append(net_if.unique_id)
            orig_net_if_ip_addr_id = net_if.ip_address_id
            net_if.ip_address_id = ip_address.id

            if orig_net_if_ip_addr_id != ip_address.id:

                net_if_audit = NetworkInterfaceAudit(object_id=net_if.id,
                                                     field='ip_address_id',
                                                     old_value=orig_net_if_ip_addr_id,
                                                     new_value=ip_address.id,
                                                     updated_by=user,
                                                     created=utcnow)
                DBSession.add(net_if_audit)

                LOG.debug('Creating audit entry for ip_address assignment '
                          'to network_interface...')
                ip_addr_audit = IpAddressAudit(object_id=ip_address.id,
                                               field='net_if_assignment',
                                               old_value='created',
                                               new_value=net_if.id,
                                               updated_by=user,
                                               created=utcnow)

                DBSession.add(ip_addr_audit)


            DBSession.add(net_if)
            DBSession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='ip_address not found')

    except MultipleResultsFound:
        msg = 'Bad request: network_interface_id is not unique: {0}'.format(net_if.id)
        return api_400(msg=msg)
    except Exception as ex:
        msg = 'Error updating ip_address: exception={0}'.format(ex)
        LOG.error(msg)
        return api_500(msg=msg)

    LOG.debug('RETURN assign_status()')
    return api_200(results=resp)

@view_config(route_name='api_ip_addresses', request_method='GET', request_param='schema=true', renderer='json')
def api_ip_addresses_schema(request):
    '''Schema document for the ip_addresses API.'''

    ip_addresses = {
    }

    return ip_addresses

# TODO: Need to create the perms if we start allowing manual updates
@view_config(route_name='api_ip_addresses', permission='ip_address_write', request_method='PUT', renderer='json')
def api_ip_addreses_write(request):
    '''Process write requests for /api/ip_addreses route.'''

    try:
        req_params = [
            'ip_address',
        ]
        opt_params = []
        params = collect_params(request, req_params, opt_params)
        params['unique_id'] = params['unique_id'].lower()

        try:
            ip_addr = find_ip_addr_by_addr(params['ip_address'])
            update_ip_addr(ip_addr, **params)
        except NoResultFound:
            net_if = create_ip_addr(**params)

        return net_if

    except Exception as ex:
        msg = 'Error writing to network_interfaces API={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

# TODO: Need to create the perms if we start allowing manual add/delete
@view_config(route_name='api_ip_address_r', permission='ip_address_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_ip_address_r', permission='ip_address_write', request_method='PUT', renderer='json')
def api_ip_address_write_attrib(request):
    '''Process write requests for the /api/ip_address/{id}/{resource} route.'''

    LOG.debug('START api_ip_address_write_attrib()')
    resource = request.matchdict['resource']
    payload = request.json_body
    auth_user = get_authenticated_user(request)

    LOG.debug('Updating {0}'.format(request.url))

    # First get the network_interfaces, then figure out what to do to it.
    ip_addr = find_ip_addr_by_id(request.matchdict['id'])
    LOG.debug('ip_addr is: {0}'.format(ip_addr))

    # List of resources allowed
    resources = [
        'undef',
    ]

    if resource in resources:
        try:
            actionable = payload[resource]
            if resource == 'undef':
                LOG.warn('Not allowed.')
                resp = []
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating ip_addresses: {0} '
                      'exception: {1}'.format(request.url, ex))
            return api_500(msg=str(ex))
    else:
        return api_501()

    return resp
