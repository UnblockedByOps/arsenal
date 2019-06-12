'''Arsenal API physical_locations.'''
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
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.physical_locations import (
    PhysicalLocation,
    PhysicalLocationAudit,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_physical_location_by_name(name):
    '''Find a physical_location by name. Returns a physical_location object if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for physical_location by name: {0}'.format(name))
    physical_location = DBSession.query(PhysicalLocation)
    physical_location = physical_location.filter(PhysicalLocation.name == name)

    return physical_location.one()

def find_physical_location_by_id(physical_location_id):
    '''Find a physical_location by id.'''

    LOG.debug('Searching for physical_location by id: {0}'.format(physical_location_id))
    physical_location = DBSession.query(PhysicalLocation)
    physical_location = physical_location.filter(PhysicalLocation.id == physical_location_id)

    return physical_location.one()

def create_physical_location(name=None,
                             updated_by=None,
                             **kwargs):
    '''Create a new physical_location.

    Required params:

    name      : A string that is the name of the physical_location.
    updated_by: A string that is the user making the update.

    Optional kwargs:

    provider    : A string that is the physical_location provider.
    address_1   : A string that is the address line 1.
    address_2   : A string that is the address line 2.
    city        : A string that is the address city.
    admin_area  : A string that is the state/province.
    country     : A string that is teh country.
    postal_code : A string that is the postal code.
    contact_name: A string that is the contat name of the data center.
    phone_number: A string that is the phone number of the data center.
    '''

    try:
        LOG.info('Creating new physical_location name: {1}'.format(name))

        utcnow = datetime.utcnow()

        physical_location = PhysicalLocation(name=name,
                                             updated_by=updated_by,
                                             created=utcnow,
                                             updated=utcnow,
                                             **kwargs)

        DBSession.add(physical_location)
        DBSession.flush()

        audit = PhysicalLocationAudit(object_id=physical_location.id,
                                      field='name',
                                      old_value='created',
                                      new_value=physical_location.name,
                                      updated_by=updated_by,
                                      created=utcnow)
        DBSession.add(audit)
        DBSession.flush()

        return physical_location
    except Exception as ex:
        msg = 'Error creating new physical_location name: {0} exception: ' \
              '{1}'.format(name, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_physical_location(physical_location, **kwargs):
    '''Update an existing physical_location.

    Required params:

    physical_location : A physical_location object.
    updated_by        : A string that is the user making the update.

    Optional kwargs:

    provider    : A string that is the physical_location provider.
    address_1   : A string that is the address line 1.
    address_2   : A string that is the address line 2.
    city        : A string that is the address city.
    admin_area  : A string that is the state/province.
    country     : A string that is teh country.
    postal_code : A string that is the postal code.
    contact_name: A string that is the contat name of the data center.
    phone_number: A string that is the phone number of the data center.
    '''

    try:
        # Convert everything that is defined to a string.
        my_attribs = kwargs.copy()
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])

        LOG.info('Updating physical_location: {0}'.format(physical_location.name))

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'name':
                LOG.debug('Skipping update to physical_location.name')
                continue
            old_value = getattr(physical_location, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating physical_location: {0} attribute: '
                          '{1} new_value: {2}'.format(physical_location.name,
                                                      attribute,
                                                      new_value))
                audit = PhysicalLocationAudit(object_id=physical_location.id,
                                              field=attribute,
                                              old_value=old_value,
                                              new_value=new_value,
                                              updated_by=my_attribs['updated_by'],
                                              created=utcnow)
                DBSession.add(audit)
                setattr(physical_location, attribute, new_value)

        DBSession.flush()

        return physical_location

    except Exception as ex:
        msg = 'Error updating physical_location name: {0} updated_by: {1} exception: ' \
              '{2}'.format(physical_location.name,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

# Routes
@view_config(route_name='api_physical_locations', request_method='GET', request_param='schema=true', renderer='json')
def api_physical_locations_schema(request):
    '''Schema document for the physical_locations API.'''

    physical_location = {
    }

    return physical_location

@view_config(route_name='api_physical_locations', permission='physical_location_write', request_method='PUT', renderer='json')
def api_physical_locations_write(request):
    '''Process write requests for /api/physical_locations route.'''

    try:
        req_params = [
            'name',
        ]
        opt_params = [
            'provider',
            'address_1',
            'address_2',
            'city',
            'admin_area',
            'country',
            'postal_code',
            'contact_name',
            'phone_number',
        ]
        params = collect_params(request, req_params, opt_params)

        try:
            physical_location = find_physical_location_by_name(params['name'])
            update_physical_location(physical_location, **params)
        except NoResultFound:
            physical_location = create_physical_location(**params)

        return physical_location

    except Exception as ex:
        msg = 'Error writing to physical_locations API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_physical_location_r', permission='physical_location_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_location_r', permission='physical_location_write', request_method='PUT', renderer='json')
def api_physical_location_write_attrib(request):
    '''Process write requests for the /api/physical_locations/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body
    auth_user = get_authenticated_user(request)

    LOG.debug('Updating {0}'.format(request.url))

    # First get the physical_location, then figure out what to do to it.
    physical_location = find_physical_location_by_id(request.matchdict['id'])
    LOG.debug('physical_location is: {0}'.format(physical_location))

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing physical_location?
    if resource in resources:
        try:
            actionable = payload[resource]
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating physical_locations: {0} exception: {1}'.format(request.url, ex))
            return api_500(msg=str(ex))
    else:
        return api_501()

    return resp
