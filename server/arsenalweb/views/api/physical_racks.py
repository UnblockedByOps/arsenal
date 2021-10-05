'''Arsenal API physical_racks.'''
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
import re
from datetime import datetime
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_500,
    api_501,
    collect_params,
    )
from arsenalweb.views.api.physical_locations import (
    find_physical_location_by_name,
    )
from arsenalweb.models.physical_racks import (
    PhysicalRack,
    PhysicalRackAudit,
    )


LOG = logging.getLogger(__name__)


# Functions
def find_physical_rack_by_name_loc(dbsession, name, physical_location_id):
    '''Find a physical_rack by name and physical_location_id. Returns
    a physical_rack object if found, raises NoResultFound otherwise.'''

    LOG.debug('Searching for physical_rack by name: %s '
              'physical_location_id: %s', name, physical_location_id)

    physical_rack = dbsession.query(PhysicalRack)
    physical_rack = physical_rack.filter(PhysicalRack.name == name)
    physical_rack = physical_rack.filter(PhysicalRack.physical_location_id == physical_location_id)

    return physical_rack.one()

def find_physical_rack_by_id(dbsession, physical_rack_id):
    '''Find a physical_rack by id.'''

    LOG.debug('Searching for physical_rack by id: %s', physical_rack_id)
    physical_rack = dbsession.query(PhysicalRack)
    physical_rack = physical_rack.filter(PhysicalRack.id == physical_rack_id)

    return physical_rack.one()

def create_physical_rack(dbsession,
                         name=None,
                         physical_location_id=None,
                         updated_by=None,
                         **kwargs):
    '''Create a new physical_rack.

    Required params:

    name      : A string that is the name of the datacenter.
    physical_location_id: An integer that represents the id of the
        physical_location the rack resides in.
    updated_by: A string that is the user making the update.

    Optional kwargs:

    server_subnet: A string that is the subnet for server addresses for
        this rack. Must be in CIDR format.
    oob_subnet   : A string that is the subnet for oob management addresses for
        this rack. Must be in CIDR format.
    '''

    try:
        LOG.info('Creating new physical_rack name: %s', name)

        utcnow = datetime.utcnow()

        my_attribs = kwargs.copy()
        for attribute in my_attribs:
            if attribute.endswith('_subnet') and my_attribs[attribute] and not validate_cidr(my_attribs[attribute]):
                msg = '{0} is not in CIDR format'.format(my_attribs[attribute])

                return api_500(msg=msg)

        physical_rack = PhysicalRack(name=name,
                                     physical_location_id=physical_location_id,
                                     updated_by=updated_by,
                                     created=utcnow,
                                     updated=utcnow,
                                     **kwargs)

        dbsession.add(physical_rack)
        dbsession.flush()

        audit = PhysicalRackAudit(object_id=physical_rack.id,
                                  field='name',
                                  old_value='created',
                                  new_value=physical_rack.name,
                                  updated_by=updated_by,
                                  created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return api_200(results=physical_rack)

    except Exception as ex:
        msg = 'Error creating new physical_rack name: {0} exception: ' \
              '{1}'.format(name, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_physical_rack(dbsession, physical_rack, **kwargs):
    '''Update an existing physical_rack.

    Required params:

    physical_rack : A physical_rack object.
    updated_by        : A string that is the user making the update.

    Optional kwargs:

    physical_location_id: An integer that represents the id of the
        physical_location the rack resides in.
    server_subnet       : A string that is the subnet for server addresses for
        this rack. Must be in CIDR format.
    oob_subnet          : A string that is the subnet for oob management addresses for
        this rack. Must be in CIDR format.
    '''

    try:
        # Convert everything that is defined to a string.
        my_attribs = kwargs.copy()
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])

        LOG.info('Updating physical_rack: %s', physical_rack.name)

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            LOG.debug('Working on attribute: %s', attribute)
            if attribute == 'name':
                LOG.debug('Skipping update to physical_rack.name')
                continue

            old_value = getattr(physical_rack, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:

                if attribute.endswith('_subnet') and not validate_cidr(my_attribs[attribute]):
                    msg = '{0} is not in CIDR format'.format(my_attribs[attribute])

                    return api_500(msg=msg)

                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating physical_rack: %s attribute: '
                          '%s new_value: %s', physical_rack.name,
                                              attribute,
                                              new_value)
                audit = PhysicalRackAudit(object_id=physical_rack.id,
                                          field=attribute,
                                          old_value=old_value,
                                          new_value=new_value,
                                          updated_by=my_attribs['updated_by'],
                                          created=utcnow)
                dbsession.add(audit)
                setattr(physical_rack, attribute, new_value)

        dbsession.flush()

        return api_200(results=physical_rack)

    except Exception as ex:
        msg = 'Error updating physical_rack name: {0} updated_by: {1} exception: ' \
              '{2}'.format(physical_rack.name,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

def validate_cidr(my_cidr):
    '''Validate that the input is valid CIDR notation'''

    LOG.debug('Validating string is in CIDR format: %s', my_cidr)
    re_cidr = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\\/(\\d|[1-2]\\d|3[0-2]))$")

    if re.match(re_cidr, my_cidr):
        LOG.debug('%s is valid CIDR notation', my_cidr)
        return True

    LOG.debug('%s is not valid CIDR notation', my_cidr)
    return False

# Routes
@view_config(route_name='api_physical_racks', request_method='GET', request_param='schema=true', renderer='json')
def api_physical_racks_schema(request):
    '''Schema document for the physical_racks API.'''

    physical_rack = {
    }

    return physical_rack

@view_config(route_name='api_physical_racks', permission='physical_rack_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_racks_write(request):
    '''Process write requests for /api/physical_racks route.'''

    try:
        req_params = [
            'name',
            'physical_location',
        ]
        opt_params = [
            'oob_subnet',
            'server_subnet',
        ]
        params = collect_params(request, req_params, opt_params)

        try:
            if isinstance(params['physical_location'], dict):
                my_pl = params['physical_location']['name']
            else:
                my_pl = params['physical_location']
            physical_location = find_physical_location_by_name(request.dbsession, my_pl)
            params['physical_location_id'] = physical_location.id
            del params['physical_location']
            try:
                physical_rack = find_physical_rack_by_name_loc(request.dbsession,
                                                               params['name'],
                                                               params['physical_location_id'])
                resp = update_physical_rack(request.dbsession, physical_rack, **params)
            except NoResultFound:
                resp = create_physical_rack(request.dbsession, **params)
        except NoResultFound:
            msg = 'physical_location not found: {0} unable to create ' \
                  'rack: {1}'.format(params['physical_location'], params['name'])
            LOG.warning(msg)
            raise NoResultFound(msg)

        return resp

    except Exception as ex:
        msg = 'Error writing to physical_racks API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_physical_rack_r', permission='physical_rack_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_physical_rack_r', permission='physical_rack_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_rack_write_attrib(request):
    '''Process write requests for the /api/physical_racks/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body

    LOG.debug('Updating %s', request.url)

    # First get the physical_rack, then figure out what to do to it.
    physical_rack = find_physical_rack_by_id(request.dbsession, request.matchdict['id'])
    LOG.debug('physical_rack is: %s', physical_rack)

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing physical_rack?
    if resource in resources:
        try:
            actionable = payload[resource]
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating physical_racks: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return []
