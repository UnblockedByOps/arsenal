'''Arsenal API physical_devices.'''
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
from arsenalweb.views.api.hardware_profiles import (
    get_hardware_profile,
    )
from arsenalweb.views.api.physical_locations import (
    find_physical_location_by_name,
    )
from arsenalweb.views.api.physical_racks import (
    find_physical_rack_by_name,
    )
from arsenalweb.views.api.physical_elevations import (
    find_physical_elevation_by_elevation,
    )
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.physical_devices import (
    PhysicalDevice,
    PhysicalDeviceAudit,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_physical_device_by_serial(serial_number):
    '''Find a physical_device by serial_number. Returns a physical_device object if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for physical_device by serial_number: {0}'.format(serial_number))
    physical_device = DBSession.query(PhysicalDevice)
    physical_device = physical_device.filter(PhysicalDevice.serial_number == serial_number)

    return physical_device.one()

def find_physical_device_by_id(physical_device_id):
    '''Find a physical_device by id.'''

    LOG.debug('Searching for physical_device by id: {0}'.format(physical_device_id))
    physical_device = DBSession.query(PhysicalDevice)
    physical_device = physical_device.filter(PhysicalDevice.id == physical_device_id)

    return physical_device.one()

def create_physical_device(serial_number=None,
                           physical_location_id=None,
                           physical_rack_id=None,
                           physical_elevation_id=None,
                           updated_by=None,
                           **kwargs):
    '''Create a new physical_device.

    Required params:

    physical_location_id : An integer representing the physical_location_id
        from the physical_locations table.
    physical_rack_id     : An integer representing the physical_rack_id
        from the physical_racks table.
    physical_elevation_id: An integer representing the physical_elevation_id
        from the physical_elevations table.
    serial_number        : A string that is the serial_number of the physical_device.
    updated_by           : A string that is the user making the update.

    Optional kwargs:

    hardware_profile_id: An integer representing the hardware_profile_id from
        the hardware_profiles table.
    oob_ip_address: A string representing the out of band IP address.
    oob_mac_address: A string representing the out of band MAC address.
    '''

    try:
        LOG.info('Creating new physical_device serial_number: {0}'.format(serial_number))

        utcnow = datetime.utcnow()

        physical_device = PhysicalDevice(serial_number=serial_number,
                                         physical_location_id=physical_location_id,
                                         physical_rack_id=physical_rack_id,
                                         physical_elevation_id=physical_elevation_id,
                                         updated_by=updated_by,
                                         created=utcnow,
                                         updated=utcnow,
                                         **kwargs)

        DBSession.add(physical_device)
        DBSession.flush()

        audit = PhysicalDeviceAudit(object_id=physical_device.id,
                                    field='serial_number',
                                    old_value='created',
                                    new_value=physical_device.serial_number,
                                    updated_by=updated_by,
                                    created=utcnow)
        DBSession.add(audit)
        DBSession.flush()

        return physical_device
    except Exception as ex:
        msg = 'Error creating new physical_device serial_number: {0} exception: ' \
              '{1}'.format(serial_number, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_physical_device(physical_device, **kwargs):
    '''Update an existing physical_device.

    Required params:

    physical_device : A physical_device object.
    updated_by      : A string that is the user making the update.

    Optional kwargs:

    hardware_profile_id: An integer representing the hardware_profile_id from
        the hardware_profiles table.
    oob_ip_address: A string representing the out of band IP address.
    oob_mac_address: A string representing the out of band MAC address.
    physical_location_id : An integer representing the physical_location_id
        from the physical_locations table.
    physical_rack_id     : An integer representing the physical_rack_id
        from the physical_racks table.
    physical_elevation_id: An integer representing the physical_elevation_id
        from the physical_elevations table.
    '''

    try:
        my_attribs = kwargs.copy()

        LOG.info('Updating physical_device: {0}'.format(physical_device.serial_number))

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'serial_number':
                LOG.debug('Skipping update to physical_device.serial_number')
                continue
            old_value = getattr(physical_device, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating physical_device: {0} attribute: '
                          '{1} new_value: {2}'.format(physical_device.serial_number,
                                                      attribute,
                                                      new_value))
                audit = PhysicalDeviceAudit(object_id=physical_device.id,
                                            field=attribute,
                                            old_value=old_value,
                                            new_value=new_value,
                                            updated_by=my_attribs['updated_by'],
                                            created=utcnow)
                DBSession.add(audit)
                setattr(physical_device, attribute, new_value)

        DBSession.flush()

        return physical_device

    except Exception as ex:
        msg = 'Error updating physical_device serial_number: {0} updated_by: {1} exception: ' \
              '{2}'.format(physical_device.serial_number,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

def convert_names_to_ids(params):
    '''Converts nice names to ids for creating/updating a physical_device.'''

    try:
        if params['hardware_profile']:
            try:
                hardware_profile = get_hardware_profile(params['hardware_profile'])
                params['hardware_profile_id'] = hardware_profile.id
                del params['hardware_profile']
            except AttributeError:
                msg = 'hardware_profile not found: {0}'.format(params['hardware_profile'])
                LOG.error(msg)
                raise NoResultFound(msg)
        if params['physical_location']:
            try:
                physical_location = find_physical_location_by_name(params['physical_location'])
                params['physical_location_id'] = physical_location.id
                LOG.debug('physical_location_id: {0}'.format(params['physical_location_id']))
                del params['physical_location']
            except NoResultFound:
                msg = 'physcial_location not found: {0}'.format(params['physical_location'])
                LOG.error(msg)
                raise NoResultFound(msg)
        if params['physical_rack']:
            try:
                physical_rack = find_physical_rack_by_name(params['physical_rack'],
                                                           params['physical_location_id'])
                params['physical_rack_id'] = physical_rack.id
                del params['physical_rack']
            except NoResultFound:
                msg = 'physcial_rack not found: {0}'.format(params['physical_rack'])
                LOG.error(msg)
                raise NoResultFound(msg)
        if params['physical_elevation']:
            try:
                physical_elevation = find_physical_elevation_by_elevation(params['physical_elevation'],
                                                                          params['physical_rack_id'])
                params['physical_elevation_id'] = physical_elevation.id
                del params['physical_elevation']
            except NoResultFound:
                msg = 'physcial_elevation not found: {0}'.format(params['physical_elevation'])
                LOG.error(msg)
                raise NoResultFound(msg)
    except:
        raise

    return params

# Routes
@view_config(route_name='api_physical_devices', request_method='GET', request_param='schema=true', renderer='json')
def api_physical_devices_schema(request):
    '''Schema document for the physical_devices API.'''

    physical_devices = {
    }

    return physical_devices

@view_config(route_name='api_physical_devices', permission='physical_device_write', request_method='PUT', renderer='json')
def api_physical_devices_write(request):
    '''Process write requests for /api/physical_devices route.'''

    try:
        req_params = [
            'serial_number',
        ]
        opt_params = [
            'hardware_profile',
            'oob_ip_address',
            'oob_mac_address',
            'physical_location',
            'physical_rack',
            'physical_elevation',
        ]
        params = collect_params(request, req_params, opt_params)
        params = convert_names_to_ids(params)

        try:
            physical_device = find_physical_device_by_serial(params['serial_number'])
            physical_device = update_physical_device(physical_device, **params)
        except NoResultFound:
            physical_device = create_physical_device(**params)

        return physical_device

    except Exception as ex:
        msg = 'Error writing to physical_devices API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_physical_device_r', permission='physical_device_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_device_r', permission='physical_device_write', request_method='PUT', renderer='json')
def api_physical_device_write_attrib(request):
    '''Process write requests for the /api/physical_devices/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body
    auth_user = get_authenticated_user(request)

    LOG.debug('Updating {0}'.format(request.url))

    # First get the physical_device, then figure out what to do to it.
    physical_device = find_physical_device_by_id(request.matchdict['id'])
    LOG.debug('physical_device is: {0}'.format(physical_device))

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing # physical_devices?
    if resource in resources:
        try:
            actionable = payload[resource]
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating physical_devices: {0} exception: {1}'.format(request.url, ex))
            return api_500(msg=str(ex))
    else:
        return api_501()

    return resp
