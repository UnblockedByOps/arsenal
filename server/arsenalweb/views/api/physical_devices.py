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
from sqlalchemy.exc import IntegrityError
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    collect_params,
    enforce_api_change_limit,
    )
from arsenalweb.views.api.hardware_profiles import (
    get_hardware_profile,
    )
from arsenalweb.views.api.physical_locations import (
    find_physical_location_by_name,
    )
from arsenalweb.views.api.physical_racks import (
    find_physical_rack_by_name_loc,
    )
from arsenalweb.views.api.physical_elevations import (
    find_physical_elevation_by_elevation,
    )
from arsenalweb.models.physical_devices import (
    PhysicalDevice,
    PhysicalDeviceAudit,
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

def find_physical_device_by_serial(dbsession, serial_number):
    '''Find a physical_device by serial_number. Returns a physical_device object if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for physical_device by serial_number: %s', serial_number)
    physical_device = dbsession.query(PhysicalDevice)
    physical_device = physical_device.filter(PhysicalDevice.serial_number == serial_number)

    return physical_device.one()

def find_physical_device_by_id(dbsession, physical_device_id):
    '''Find a physical_device by id.'''

    LOG.debug('Searching for physical_device by id: %s', physical_device_id)
    physical_device = dbsession.query(PhysicalDevice)
    physical_device = physical_device.filter(PhysicalDevice.id == physical_device_id)

    return physical_device.one()

def create_physical_device(dbsession,
                           serial_number=None,
                           mac_address_1=None,
                           physical_location_id=None,
                           physical_rack_id=None,
                           physical_elevation_id=None,
                           status_id=None,
                           updated_by=None,
                           **kwargs):
    '''Create a new physical_device.

    Required params:

    hardware_profile_id: An integer representing the hardware_profile_id from
        the hardware_profiles table.
    mac_address_1: A string representing the MAC address of the first interface.
    physical_location_id : An integer representing the physical_location_id
        from the physical_locations table.
    physical_rack_id     : An integer representing the physical_rack_id
        from the physical_racks table.
    physical_elevation_id: An integer representing the physical_elevation_id
        from the physical_elevations table.
    serial_number        : A string that is the serial_number of the physical_device.
    status_id            : An integer representing the status_id from the statuses table.
    updated_by           : A string that is the user making the update.

    Optional kwargs:

    mac_address_2: A string representing the MAC address of the second interface.
    oob_ip_address: A string representing the out of band IP address.
    oob_mac_address: A string representing the out of band MAC address.
    '''

    try:
        my_serial_number = serial_number.upper()
    except AttributeError:
        LOG.debug("serial_number is None type.")
        my_serial_number = serial_number

    try:
        LOG.info('Creating new physical_device serial_number: %s', my_serial_number)

        utcnow = datetime.utcnow()

        mac_address_1 = mac_address_1.lower()

        try:
            kwargs['mac_address_2'] = kwargs['mac_address_2'].lower()
        except (AttributeError, KeyError):
            pass

        try:
            kwargs['oob_mac_address'] = kwargs['oob_mac_address'].lower()
        except (AttributeError, KeyError):
            pass

        physical_device = PhysicalDevice(serial_number=my_serial_number,
                                         mac_address_1=mac_address_1,
                                         physical_location_id=physical_location_id,
                                         physical_rack_id=physical_rack_id,
                                         physical_elevation_id=physical_elevation_id,
                                         status_id=status_id,
                                         updated_by=updated_by,
                                         created=utcnow,
                                         updated=utcnow,
                                         **kwargs)

        dbsession.add(physical_device)
        dbsession.flush()

        audit = PhysicalDeviceAudit(object_id=physical_device.id,
                                    field='serial_number',
                                    old_value='created',
                                    new_value=physical_device.serial_number,
                                    updated_by=updated_by,
                                    created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return api_200(results=physical_device)

    except IntegrityError:
        msg = 'Physical elevation is already occupied, move the existing ' \
              'physical_device first.'
        LOG.error(msg)
        raise Exception(msg)
    except Exception as ex:
        msg = 'Error creating new physical_device serial_number: {0} exception: ' \
              '{1}'.format(my_serial_number, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_physical_device(dbsession, physical_device, **kwargs):
    '''Update an existing physical_device.

    Required params:

    physical_device : A physical_device object.
    updated_by      : A string that is the user making the update.

    Optional kwargs:

    hardware_profile_id: An integer representing the hardware_profile_id from
        the hardware_profiles table.
    mac_address_1: A string representing the MAC address of the first interface.
    mac_address_2: A string representing the MAC address of the second interface.
    oob_ip_address: A string representing the out of band IP address.
    oob_mac_address: A string representing the out of band MAC address.
    physical_location_id : An integer representing the physical_location_id
        from the physical_locations table.
    physical_rack_id     : An integer representing the physical_rack_id
        from the physical_racks table.
    physical_elevation_id: An integer representing the physical_elevation_id
        from the physical_elevations table.
    status_id: An integer representing the status_id from the statuses table.
    '''

    try:
        my_attribs = kwargs.copy()

        LOG.info('Updating physical_device: %s', physical_device.serial_number)

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'serial_number':
                LOG.debug('Skipping update to physical_device.serial_number')
                continue
            old_value = getattr(physical_device, attribute)

            if attribute in ["mac_address_1", "mac_address_2", "oob_mac_address"]:
                try:
                    new_value = my_attribs[attribute].lower()
                except (AttributeError, KeyError):
                    new_value = my_attribs[attribute]
            else:
                new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating physical_device: %s attribute: '
                          '%s new_value: %s', physical_device.serial_number,
                                              attribute,
                                              new_value)
                audit = PhysicalDeviceAudit(object_id=physical_device.id,
                                            field=attribute,
                                            old_value=old_value,
                                            new_value=new_value,
                                            updated_by=my_attribs['updated_by'],
                                            created=utcnow)
                dbsession.add(audit)
                setattr(physical_device, attribute, new_value)

        dbsession.flush()

        return api_200(results=physical_device)

    except IntegrityError:
        msg = 'Physical elevation is already occupied, move the existing ' \
              'physical_device first.'
        LOG.error(msg)
        raise Exception(msg)
    except Exception as ex:
        msg = 'Error updating physical_device serial_number: {0} updated_by: {1} exception: ' \
              '{2}'.format(physical_device.serial_number,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

def convert_names_to_ids(dbsession, params):
    '''Converts nice names to ids for creating/updating a physical_device.'''

    try:
        try:
            try:
                physical_location = params['physical_location']['name']
            except TypeError:
                physical_location = params['physical_location']

            physical_location = find_physical_location_by_name(dbsession, physical_location)
            params['physical_location_id'] = physical_location.id
            LOG.debug('physical_location_id: %s', params['physical_location_id'])
            del params['physical_location']
        except NoResultFound:
            msg = 'physical_location not found: {0}'.format(params['physical_location'])
            LOG.error(msg)
            raise NoResultFound(msg)

        try:
            try:
                physical_rack_name = params['physical_rack']['name']
            except TypeError:
                physical_rack_name = params['physical_rack']
            physical_rack = find_physical_rack_by_name_loc(dbsession,
                                                           physical_rack_name,
                                                           params['physical_location_id'])
            params['physical_rack_id'] = physical_rack.id
            del params['physical_rack']
        except NoResultFound:
            msg = 'physical_rack not found: {0}'.format(params['physical_rack'])
            LOG.error(msg)
            raise NoResultFound(msg)

        try:
            try:
                physical_elevation_el = params['physical_elevation']['elevation']
            except TypeError:
                physical_elevation_el = params['physical_elevation']
            physical_elevation = find_physical_elevation_by_elevation(dbsession,
                                                                      physical_elevation_el,
                                                                      params['physical_rack_id'])
            params['physical_elevation_id'] = physical_elevation.id
            del params['physical_elevation']
        except NoResultFound:
            msg = 'physical_elevation not found: {0}'.format(params['physical_elevation'])
            LOG.error(msg)
            raise NoResultFound(msg)

        try:
            try:
                status_name = params['status']['name']
            except TypeError:
                status_name = params['status']

            if not status_name:
                status_name = 'available'

            status = find_status_by_name(dbsession, status_name)
            params['status_id'] = status.id
            try:
                del params['status']
            except KeyError:
                pass
        except NoResultFound:
            msg = 'Unable to determine status of physical_device.'
            LOG.error(msg)
            raise NoResultFound(msg)

        if params['hardware_profile']:
            try:
                hw_profile_name = params['hardware_profile']['name']
            except TypeError:
                hw_profile_name = params['hardware_profile']
            try:
                hardware_profile = get_hardware_profile(dbsession, hw_profile_name)
                params['hardware_profile_id'] = hardware_profile.id
                del params['hardware_profile']
            except AttributeError:
                msg = 'hardware_profile not found: {0}'.format(params['hardware_profile'])
                LOG.error(msg)
                raise NoResultFound(msg)

    except Exception as ex:
        LOG.error(repr(ex))
        raise

    return params

# Routes
@view_config(route_name='api_physical_devices', request_method='GET', request_param='schema=true', renderer='json')
def api_physical_devices_schema(request):
    '''Schema document for the physical_devices API.'''

    physical_devices = {
    }

    return physical_devices

@view_config(route_name='api_physical_devices', permission='physical_device_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_devices_write(request):
    '''Process write requests for /api/physical_devices route.'''

    try:
        req_params = [
            'hardware_profile',
            'mac_address_1',
            'physical_elevation',
            'physical_location',
            'physical_rack',
            'serial_number',
        ]
        opt_params = [
            'mac_address_2',
            'oob_ip_address',
            'oob_mac_address',
            'status',
        ]
        params = collect_params(request, req_params, opt_params)
        try:
            params = convert_names_to_ids(request.dbsession, params)
            LOG.debug('params are: {0}'.format(params))
        except NoResultFound as ex:
            msg = 'Error writing to physical_devices API: {0}'.format(ex)
            LOG.error(msg)
            return api_404(msg=msg)

        try:
            my_serial_number = params['serial_number'].upper()
        except AttributeError:
            LOG.debug("serial_number is None type.")
            my_serial_number = params['serial_number']

        try:
            physical_device = find_physical_device_by_serial(request.dbsession,
                                                             my_serial_number)
            physical_device = update_physical_device(request.dbsession, physical_device, **params)
        except NoResultFound:
            physical_device = create_physical_device(request.dbsession, **params)

        return physical_device

    except Exception as ex:
        msg = 'Error writing to physical_devices API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_physical_device_r', permission='physical_device_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_physical_device_r', permission='physical_device_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_device_write_attrib(request):
    '''Process write requests for the /api/physical_devices/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body

    LOG.debug('Updating %s', request.url)

    # First get the physical_device, then figure out what to do to it.
    physical_device = find_physical_device_by_id(request.dbsession, request.matchdict['id'])
    LOG.debug('physical_device is: %s', physical_device)

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing # physical_devices?
    if resource in resources:
        try:
            actionable = payload[resource]

            item_count = len(actionable)
            denied = enforce_api_change_limit(request, item_count)
            if denied:
                return api_400(msg=denied)

        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating physical_devices: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return []
