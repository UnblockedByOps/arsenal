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
from pyramid.view import view_config
from pyramid.response import Response
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    log,
    )
from arsenalweb.views.api import (
    get_api_attribute,
    api_read_by_id,
    api_read_by_params,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    Status,
    )


@view_config(route_name='api_statuses', request_method='GET', request_param='schema=true', renderer='json')
def api_statuses_schema(request):
    """Schema document for the statuses API."""

    ng = {
    }

    return ng


@view_config(route_name='api_status_r', request_method='GET', renderer='json')
def api_status_read_attrib(request):
    """Process read requests for the /api/statuses/{id}/{resource} route."""

    return get_api_attribute(request, 'Status')


@view_config(route_name='api_status', request_method='GET', renderer='json')
def api_status_read_id(request):
    """Process read requests for the /api/statuses/{id} route."""

    return api_read_by_id(request, 'Status')


@view_config(route_name='api_statuses', request_method='GET', renderer='json')
def api_status_read(request):
    """Process read requests for the /api/statuses route."""

    return api_read_by_params(request, 'Status')


@view_config(route_name='api_statuses', permission='api_write', request_method='PUT', renderer='json')
def api_status_write(request):
    """Process write requests for /apistatusesnode_groups route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body
        status_name = payload['status_name']
        description = payload['description']

        log.debug('Searching for statuses status_name={0},description={1}'.format(status_name, description))
        try:
            s = DBSession.query(Status.status_name==status_name)
            s = s.one()
        except NoResultFound:
            try:
                log.info('Creating new status status_name={0},description={1}'.format(status_name, description))
                utcnow = datetime.utcnow()

                s = Status(status_name=status_name,
                           description=description,
                           updated_by=au['user_id'],
                           created=utcnow,
                           updated=utcnow)

                DBSession.add(s)
                DBSession.flush()
            except Exception, e:
                log.error('Error creating status status_name={0},description={1},exception={2}'.format(status_name, description, e))
                raise
        else:
            try:
                log.info('Updating status_name={0},description={1}'.format(status_name, description))

                s.status_name = payload['status_name']
                s.description = payload['description']
                s.updated_by=au['user_id']

                DBSession.flush()

            except Exception, e:
                log.error('Error updating status status_name={0},description={1},exception={2}'.format(status_name, description, e))
                raise

        return s

    except Exception, e:
        log.error('Error writing to statuses API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_status', permission='api_write', request_method='DELETE', renderer='json')
def api_statuses_delete_id(request):
    """Process delete requests for the /api/statuses/{id} route."""

    return api_delete_by_id(request, 'Status')


@view_config(route_name='api_statuses', permission='api_write', request_method='DELETE', renderer='json')
def api_status_delete(request):
    """Process delete requests for the /api/statuses route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'Status')


