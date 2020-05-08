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
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.models.statuses import (
    Status,
    StatusAudit,
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
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )
from arsenalweb.views.api.data_centers import (
    find_data_center_by_id,
    )

LOG = logging.getLogger(__name__)

def find_status_by_name(status_name):
    '''Find a status by name.'''

    status = DBSession.query(Status)
    status = status.filter(Status.name == status_name)

    return status.one()

def find_status_by_id(status_id):
    '''Find a status by id.'''

    status = DBSession.query(Status)
    status = status.filter(Status.id == status_id)

    return status.one()

def create_status(name, description, user_id):
    '''Create a new status.'''

    try:
        LOG.info('Creating new status name={0},description={1}'.format(name,
                                                                       description))
        utcnow = datetime.utcnow()

        status = Status(name=name,
                        description=description,
                        updated_by=user_id,
                        created=utcnow,
                        updated=utcnow)

        DBSession.add(status)
        DBSession.flush()

        status_audit = StatusAudit(object_id=status.id,
                                   field='name',
                                   old_value='created',
                                   new_value=status.name,
                                   updated_by=user_id,
                                   created=utcnow)
        DBSession.add(status_audit)
        DBSession.flush()

    except Exception, ex:
        msg = 'Error creating status name={0},description={1},' \
              'exception={2}'.format(name, description, ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return status

def assign_status(status, actionables, resource, user):
    '''Assign actionable_ids to a status.'''

    LOG.debug('START assign_status()')
    resp = {status.name: []}
    try:

        utcnow = datetime.utcnow()

        with DBSession.no_autoflush:
            for actionable_id in actionables:
                if resource == 'nodes':
                    my_obj = find_node_by_id(actionable_id)
                elif resource == 'data_centers':
                    my_obj = find_data_center_by_id(actionable_id)
                resp[status.name].append(my_obj.name)

                orig_status_id = my_obj.status_id
                orig_status = find_status_by_id(my_obj.status_id)
                LOG.debug('START assign_status() update status_id')
                my_obj.status_id = status.id
                LOG.debug('END assign_status() update status_id')
                if orig_status_id != status.id:
                    LOG.debug('START assign_status() create audit')
                    node_audit = NodeAudit(object_id=my_obj.id,
                                           field='status',
                                           old_value=orig_status.name,
                                           new_value=status.name,
                                           updated_by=user,
                                           created=utcnow)
                    DBSession.add(node_audit)
                    LOG.debug('END assign_status() create audit')

            LOG.debug('START assign_status() session add')
            DBSession.add(my_obj)
            LOG.debug('END assign_status() session add')
            LOG.debug('START assign_status() session flush')
            DBSession.flush()
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

# api_register permission is so that kaboom can update status.
@view_config(route_name='api_status_r', permission='api_register', request_method='PUT', renderer='json')
def api_status_write_attrib(request):
    '''Process write requests for the /api/statuses/{id}/{resource} route.'''

    LOG.debug('START api_status_write_attrib()')
    try:
        resource = request.matchdict['resource']
        payload = request.json_body
        auth_user = get_authenticated_user(request)

        LOG.debug('Updating {0}'.format(request.url))

        # First get the status, then figure out what to do to it.
        status = find_status_by_id(request.matchdict['id'])
        LOG.debug('status is: {0}'.format(status))

        # List of resources allowed
        resources = [
            'nodes',
            'data_centers',
        ]

        if resource in resources:
            try:
                actionable = payload[resource]
                resp = assign_status(status, actionable, resource, auth_user['user_id'])
            except KeyError:
                msg = 'Missing required parameter: {0}'.format(resource)
                return api_400(msg=msg)
            except Exception as ex:
                msg = 'Error updating status={0},exception={1}'.format(request.url, ex)
                LOG.error(msg)
                return api_500(msg=msg)
        else:
            return api_501()

        LOG.debug('RETURN api_status_write_attrib()')
        return resp
    except Exception as ex:
        msg = 'Error updating status={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_statuses', permission='api_write', request_method='PUT', renderer='json')
def api_status_write(request):
    '''Process write requests for /api/statuses route.'''

    try:
        auth_user = get_authenticated_user(request)
        payload = request.json_body
        name = payload['name'].rstrip()
        description = payload['description'].rstrip()

        LOG.debug('Searching for statuses name={0},description={1}'.format(name,
                                                                           description))
        try:
            status = DBSession.query(Status)
            status = status.filter(Status.name == name)
            status = status.one()

            try:
                LOG.info('Updating name={0},description={1}'.format(name,
                                                                    description))

                status.name = name
                status.description = description
                status.updated_by = auth_user['user_id']

                DBSession.flush()

            except Exception, ex:
                msg = 'Error updating status name={0},description={1},' \
                      'exception={2}'.format(name, description, ex)
                LOG.error(msg)
                return api_500(msg=msg)

        except NoResultFound:

            status = create_status(name, description, auth_user['user_id'])

        return api_200(results=status)

    except Exception, ex:
        msg = 'Error writing to statuses API={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)
