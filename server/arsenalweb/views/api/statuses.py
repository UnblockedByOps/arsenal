'''Arsenal API Statuses.'''
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
from arsenalweb.models.data_centers import (
    DataCenterAudit,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.models.statuses import (
    Status,
    StatusAudit,
    )
from arsenalweb.models.physical_devices import (
    PhysicalDeviceAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    collect_params,
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )
from arsenalweb.views.api.data_centers import (
    find_data_center_by_id,
    )
from arsenalweb.views.api.physical_devices import (
    update_physical_device,
    find_physical_device_by_id,
    )

LOG = logging.getLogger(__name__)

def find_status_by_name(dbsession, status_name):
    '''Find a status by name.'''

    LOG.debug('Searching for statuses name: %s', status_name)

    status = dbsession.query(Status)
    status = status.filter(Status.name == status_name)

    return status.one()

def find_status_by_id(dbsession, status_id):
    '''Find a status by id.'''

    status = dbsession.query(Status)
    status = status.filter(Status.id == status_id)

    return status.one()

def create_status(dbsession, name=None, description=None, user_id=None):
    '''Create a new status.'''

    try:
        LOG.info('Creating new status name: %s description: %s', name, description)
        utcnow = datetime.utcnow()

        status = Status(name=name,
                        description=description,
                        updated_by=user_id,
                        created=utcnow,
                        updated=utcnow)

        dbsession.add(status)
        dbsession.flush()

        status_audit = StatusAudit(object_id=status.id,
                                   field='name',
                                   old_value='created',
                                   new_value=status.name,
                                   updated_by=user_id,
                                   created=utcnow)
        dbsession.add(status_audit)
        dbsession.flush()

    except Exception as ex:
        msg = 'Error creating status name={0},description={1},' \
              'exception={2}'.format(name, description, ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return status

def update_status(dbsession, status, **kwargs):
    '''Update an existing status.

    Required params:

    status     : A status object.
    description: A string representing the description of this status.
    updated_by : A string that is the user making the update.
    '''

    try:
        my_attribs = kwargs.copy()

        LOG.debug('Updating status: %s', status.name)

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'name':
                LOG.debug('Skipping update to status.name')
                continue
            old_value = getattr(status, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating status: %s attribute: '
                          '%s new_value: %s', status.name,
                                              attribute,
                                              new_value)
                audit = StatusAudit(object_id=status.id,
                                    field=attribute,
                                    old_value=old_value,
                                    new_value=new_value,
                                    updated_by=my_attribs['updated_by'],
                                    created=utcnow)
                dbsession.add(audit)
                setattr(status, attribute, new_value)

        dbsession.flush()

        return api_200(results=status)

    except Exception as ex:
        msg = 'Error updating status name: {0} updated_by: {1} exception: ' \
              '{2}'.format(status.name,
                           my_attribs['updated_by'],
                           repr(ex))
        LOG.error(msg)
        raise

def assign_status(dbsession, status, actionables, resource, user, settings):
    '''Assign actionable_ids to a status.'''

    LOG.debug('START assign_status()')
    resp = {status.name: []}
    try:

        utcnow = datetime.utcnow()

        with dbsession.no_autoflush:
            for actionable_id in actionables:

                if resource == 'nodes':
                    my_obj = find_node_by_id(dbsession, actionable_id)
                elif resource == 'data_centers':
                    my_obj = find_data_center_by_id(dbsession, actionable_id)
                elif resource == 'physical_devices':
                    my_obj = find_physical_device_by_id(dbsession, actionable_id)

                if resource == 'physical_devices':
                    resp[status.name].append(my_obj.serial_number)
                else:
                    resp[status.name].append(my_obj.name)

                orig_status_id = my_obj.status_id
                orig_status = find_status_by_id(dbsession, my_obj.status_id)
                LOG.debug('START assign_status() update status_id')
                my_obj.status_id = status.id
                LOG.debug('END assign_status() update status_id')

                if orig_status_id != status.id:
                    LOG.debug('START assign_status() create audit')

                    my_obj.updated = utcnow
                    my_obj.updated_by = user

                    if resource == 'nodes':

                        if my_obj.physical_device:

                            try:
                                pd_status = settings['arsenal.node_hw_map.{0}'.format(status.name)]
                                av = find_status_by_name(dbsession, pd_status)
                                final_status_id = av.id

                                pd_params = {
                                    'status_id': final_status_id,
                                    'updated_by': user,
                                }

                                update_physical_device(dbsession,
                                                       my_obj.physical_device,
                                                       **pd_params)

                            except AttributeError:
                                LOG.debug('No physical_device status map attribute defined in '
                                          'config for node status: %s', status.name)

                        node_audit = NodeAudit(object_id=my_obj.id,
                                               field='status',
                                               old_value=orig_status.name,
                                               new_value=status.name,
                                               updated_by=user,
                                               created=utcnow)
                        dbsession.add(node_audit)

                    elif resource == 'data_centers':

                        dc_audit = DataCenterAudit(object_id=my_obj.id,
                                                   field='status',
                                                   old_value=orig_status.name,
                                                   new_value=status.name,
                                                   updated_by=user,
                                                   created=utcnow)
                        dbsession.add(dc_audit)

                    elif resource == 'physical_devices':

                        pd_audit = PhysicalDeviceAudit(object_id=my_obj.id,
                                                       field='status',
                                                       old_value=orig_status.name,
                                                       new_value=status.name,
                                                       updated_by=user,
                                                       created=utcnow)
                        dbsession.add(pd_audit)

                    LOG.debug('END assign_status() create audit')

            LOG.debug('START assign_status() session add')
            dbsession.add(my_obj)
            LOG.debug('END assign_status() session add')
            LOG.debug('START assign_status() session flush')
            dbsession.flush()
            LOG.debug('END assign_status() session flush')

    except (NoResultFound, AttributeError):
        return api_404(msg='status not found')

    except MultipleResultsFound:
        msg = 'Bad request: id is not unique: {0}'.format(actionable_id)
        return api_400(msg=msg)
    except Exception as ex:
        msg = 'Error updating status: exception={0}'.format(ex)
        LOG.error(msg)
        return api_500(msg=msg)

    LOG.debug('RETURN assign_status()')
    return api_200(results=resp)

@view_config(route_name='api_statuses', request_method='GET', request_param='schema=true', renderer='json')
def api_statuses_schema(request):
    '''Schema document for the statuses API.'''

    status = {
    }

    return status

@view_config(route_name='api_status_r', permission='status_write', request_method='PUT', renderer='json', require_csrf=False)
def api_status_write_attrib(request):
    '''Process write requests for the /api/statuses/{id}/{resource} route.'''

    LOG.debug('START api_status_write_attrib()')
    try:
        resource = request.matchdict['resource']
        payload = request.json_body
        user = request.identity

        LOG.debug('Updating %s', request.url)

        # First get the status, then figure out what to do to it.
        status = find_status_by_id(request.dbsession, request.matchdict['id'])
        LOG.debug('status is: %s', status)

        # List of resources allowed
        resources = [
            'nodes',
            'data_centers',
            'physical_devices',
        ]

        if resource in resources:
            try:
                actionable = payload[resource]
                settings = request.registry.settings
                resp = assign_status(request.dbsession,
                                     status,
                                     actionable,
                                     resource,
                                     user['name'],
                                     settings)
            except KeyError:
                msg = 'Missing required parameter: {0}'.format(resource)
                return api_400(msg=msg)
            except Exception as ex:
                msg = 'Error updating status: {0} exception: {1}'.format(request.url, ex)
                LOG.error(msg)
                return api_500(msg=msg)
        else:
            return api_501()

        LOG.debug('RETURN api_status_write_attrib()')
        return resp
    except Exception as ex:
        msg = 'Error updating status: {0},exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_statuses', permission='api_write', request_method='PUT', renderer='json', require_csrf=False)
def api_status_write(request):
    '''Process write requests for /api/statuses route.'''

    try:
        req_params = [
            'name',
            'description',
        ]
        opt_params = []
        params = collect_params(request, req_params, opt_params)
        try:
            status = find_status_by_name(request.dbsession, params['name'])
            status = update_status(request.dbsession, status, **params)
        except NoResultFound:
            status = create_status(request.dbsession, **params)

        return status

    except Exception as ex:
        msg = 'Error writing to statuses API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)
