'''Arsenal API physical_elevations.'''
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
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_500,
    api_501,
    collect_params,
    enforce_api_change_limit,
    )
from arsenalweb.views.api.physical_racks import (
    find_physical_rack_by_name_loc,
    )
from arsenalweb.views.api.physical_locations import (
    find_physical_location_by_name,
    )
from arsenalweb.models.physical_elevations import (
    PhysicalElevation,
    PhysicalElevationAudit,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_physical_elevation_by_elevation(dbsession, elevation, physical_rack_id):
    '''Find a physical_elevation by elevation and physical_rack_id. Returns
    a physical_elevation object if found, raises NoResultFound otherwise.'''

    LOG.debug('Searching for physical_elevation by elevation: %s '
              'physical_rack_id: %s', elevation, physical_rack_id)
    physical_elevation = dbsession.query(PhysicalElevation)
    physical_elevation = physical_elevation.filter(PhysicalElevation.elevation == elevation)
    physical_elevation = physical_elevation.filter(PhysicalElevation.physical_rack_id == physical_rack_id)

    return physical_elevation.one()

def find_physical_elevation_by_id(dbsession, physical_elevation_id):
    '''Find a physical_elevation by id.'''

    LOG.debug('Searching for physical_elevation by id: %s', physical_elevation_id)
    physical_elevation = dbsession.query(PhysicalElevation)
    physical_elevation = physical_elevation.filter(PhysicalElevation.id == physical_elevation_id)

    return physical_elevation.one()

def create_physical_elevation(dbsession,
                              elevation=None,
                              physical_rack_id=None,
                              updated_by=None,
                              **kwargs):
    '''Create a new physical_elevation.

    Required params:

    elevation      : A string that is the elevation of the rack.
    physical_rack_id: An integer that represents the id of the
        physical_rack the elevation resides in.
    updated_by: A string that is the user making the update.

    Optional kwargs:

    None yet.
    '''

    try:
        LOG.info('Creating new physical_elevation name: %s physical_rack_id: '
                 '%s', elevation, physical_rack_id)

        utcnow = datetime.utcnow()

        physical_elevation = PhysicalElevation(elevation=elevation,
                                               physical_rack_id=physical_rack_id,
                                               updated_by=updated_by,
                                               created=utcnow,
                                               updated=utcnow,
                                               **kwargs)

        dbsession.add(physical_elevation)
        dbsession.flush()

        audit = PhysicalElevationAudit(object_id=physical_elevation.id,
                                       field='elevation',
                                       old_value='created',
                                       new_value=physical_elevation.elevation,
                                       updated_by=updated_by,
                                       created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return api_200(results=physical_elevation)

    except Exception as ex:
        msg = 'Error creating new physical_elevation elevation: {0} exception: ' \
              '{1}'.format(elevation, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_physical_elevation(dbsession, physical_elevation, **kwargs):
    '''Update an existing physical_elevation.

    Required params:

    physical_elevation : A physical_elevation object.
    updated_by        : A string that is the user making the update.

    Optional kwargs:

    physical_rack_id: An integer that represents the id of the
        physical_rack the elevation resides in.
    '''

    try:
        LOG.info('Updating physical_elevation: %s', physical_elevation.elevation)

        utcnow = datetime.utcnow()

        for attribute in kwargs:
            if attribute == 'elevation':
                LOG.debug('Skipping update to physical_elevation.elevation')
                continue
            old_value = getattr(physical_elevation, attribute)
            new_value = kwargs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Types old_value: %s new_value: %s', type(old_value),
                                                               type(new_value))
                LOG.debug('Updating physical_elevation: %s attribute: '
                          '%s new_value: %s', physical_elevation.elevation,
                                              attribute,
                                              new_value)
                audit = PhysicalElevationAudit(object_id=physical_elevation.id,
                                               field=attribute,
                                               old_value=old_value,
                                               new_value=new_value,
                                               updated_by=kwargs['updated_by'],
                                               created=utcnow)
                dbsession.add(audit)
                setattr(physical_elevation, attribute, new_value)

        dbsession.flush()

        return api_200(results=physical_elevation)

    except Exception as ex:
        msg = 'Error updating physical_elevation name: {0} updated_by: {1} exception: ' \
              '{2}'.format(physical_elevation.elevation,
                           kwargs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

# Routes
@view_config(route_name='api_physical_elevations', request_method='GET', request_param='schema=true', renderer='json')
def api_physical_elevations_schema(request):
    '''Schema document for the physical_elevations API.'''

    physical_elevation = {
    }

    return physical_elevation

@view_config(route_name='api_physical_elevations', permission='physical_elevation_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_elevations_write(request):
    '''Process write requests for /api/physical_elevations route.'''

    try:
        req_params = [
            'elevation',
            'physical_location',
            'physical_rack',
        ]
        opt_params = []
        params = collect_params(request, req_params, opt_params)

        try:
            physical_location = find_physical_location_by_name(request.dbsession, params['physical_location'])
            del params['physical_location']

            physical_rack = find_physical_rack_by_name_loc(request.dbsession,
                                                           params['physical_rack'],
                                                           physical_location.id)
            params['physical_rack_id'] = physical_rack.id
            del params['physical_rack']

            try:
                physical_el = find_physical_elevation_by_elevation(request.dbsession,
                                                                   params['elevation'],
                                                                   params['physical_rack_id'])
                resp = update_physical_elevation(request.dbsession, physical_el, **params)
            except NoResultFound:
                resp = create_physical_elevation(request.dbsession, **params)
        except:
            raise

        return resp

    except Exception as ex:
        msg = 'Error writing to physical_racks API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_physical_elevation_r', permission='physical_elevation_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_physical_elevation_r', permission='physical_elevation_write', request_method='PUT', renderer='json', require_csrf=False)
def api_physical_elevation_write_attrib(request):
    '''Process write requests for the /api/physical_elevations/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body

    LOG.debug('Updating %s', request.url)

    # First get the physical_elevation, then figure out what to do to it.
    physical_elevation = find_physical_elevation_by_id(request.dbsession, request.matchdict['id'])
    LOG.debug('physical_elevation is: %s', physical_elevation)

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing physical_elevation?
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
            LOG.error('Error updating physical_elevations: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return []
