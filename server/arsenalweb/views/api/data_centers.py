'''Arsenal API data_centers.'''
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
    )
from arsenalweb.models.data_centers import (
    DataCenter,
    DataCenterAudit,
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

def find_data_center_by_name(dbsession, name):
    '''Find a data_center by name. Returns a data_center object if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for datacenter by name: %s', name)
    data_center = dbsession.query(DataCenter)
    data_center = data_center.filter(DataCenter.name == name)

    return data_center.one()

def find_data_center_by_id(dbsession, data_center_id):
    '''Find a data_center by id.'''

    LOG.debug('Searching for datacenter by id: %s', data_center_id)
    data_center = dbsession.query(DataCenter)
    data_center = data_center.filter(DataCenter.id == data_center_id)

    return data_center.one()

def create_data_center(dbsession, name=None, updated_by=None, **kwargs):
    '''Create a new data_center.

    Required params:

    name      : A string that is the name of the datacenter.
    updated_by: A string that is the user making the update.

    Optional kwargs:

    status_id   : An integer representing the status_id from the statuses table.
                  If not sent, the data_center will be set to status_id 2.
    '''

    try:
        LOG.info('Creating new data_center name: %s', name)

        utcnow = datetime.utcnow()

        # Set status to setup if the client doesn't send it.
        try:
            stat = kwargs['status']
            LOG.debug('status keyword sent: %s', stat)
            my_status = find_status_by_name(dbsession, stat)
            kwargs['status_id'] = my_status.id
            del kwargs['status']
        except KeyError:
            if 'status_id' not in kwargs or not kwargs['status_id']:
                LOG.debug('status_id not present, setting status_id to 2')
                kwargs['status_id'] = 2

        data_center = DataCenter(name=name,
                                 updated_by=updated_by,
                                 created=utcnow,
                                 updated=utcnow,
                                 **kwargs)

        dbsession.add(data_center)
        dbsession.flush()

        audit = DataCenterAudit(object_id=data_center.id,
                                field='name',
                                old_value='created',
                                new_value=data_center.name,
                                updated_by=updated_by,
                                created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return api_200(results=data_center)

    except Exception as ex:
        msg = 'Error creating new data_center name: {0} exception: {1}'.format(name,
                                                                               ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_data_center(dbsession, data_center, **kwargs):
    '''Update an existing data_center.

    Required params:

    data_center: A string that is the name of the data_center.
    updated_by : A string that is the user making the update.

    Optional kwargs:

    status_id   : An integer representing the status_id from the statuses table.
    '''

    try:
        # Convert everything that is defined to a string.
        my_attribs = kwargs.copy()
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])

        LOG.info('Updating data_center: %s', data_center.name)

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'name':
                LOG.debug('Skipping update to data_center.name.')
                continue
            old_value = getattr(data_center, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating data_center: %s attribute: '
                          '%s new_value: %s', data_center.name, attribute, new_value)
                audit = DataCenterAudit(object_id=data_center.id,
                                        field=attribute,
                                        old_value=old_value,
                                        new_value=new_value,
                                        updated_by=my_attribs['updated_by'],
                                        created=utcnow)
                dbsession.add(audit)
                setattr(data_center, attribute, new_value)

        dbsession.flush()

        return api_200(results=data_center)

    except Exception as ex:
        msg = 'Error updating data_center name: {0} updated_by: {1} exception: ' \
              '{2}'.format(data_center.name,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

# Routes
@view_config(route_name='api_data_centers', request_method='GET', request_param='schema=true', renderer='json')
def api_data_centers_schema(request):
    '''Schema document for the data_centers API.'''

    data_centers = {
    }

    return data_centers

@view_config(route_name='api_data_centers', permission='data_center_write', request_method='PUT', renderer='json', require_csrf=False)
def api_data_centers_write(request):
    '''Process write requests for /api/data_centers route.'''

    try:
        req_params = [
            'name',
        ]
        opt_params = [
            'status',
        ]
        params = collect_params(request, req_params, opt_params)

        try:
            data_center = find_data_center_by_name(request.dbsession, params['name'])
            update_data_center(request.dbsession, data_center, **params)
        except NoResultFound:
            data_center = create_data_center(request.dbsession, **params)

        return data_center

    except Exception as ex:
        msg = 'Error writing to data_centers API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_data_center_r', permission='data_center_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_data_center_r', permission='data_center_write', request_method='PUT', renderer='json', require_csrf=False)
def api_data_center_write_attrib(request):
    '''Process write requests for the /api/data_centers/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body

    LOG.debug('Updating %s', request.url)

    # First get the data_center, then figure out what to do to it.
    data_center = find_data_center_by_id(request, request.matchdict['id'])
    LOG.debug('data_center is: %s', data_center)

    # List of resources allowed
    resources = [
        'nothing_yet',
    ]

    # There's nothing to do here yet. Maye add updates to existing datacenters?
    if resource in resources:
        try:
            actionable = payload[resource]
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating data_centers: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return []
