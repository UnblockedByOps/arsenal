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
    OperatingSystem,
    )

def create_operating_system(variant, version_number, architecture, description, user_id):
    """ """
    try:
        log.info('Creating new operating_system variant={0},version_number={1},architecture={2},description={3}'.format(variant, version_number, architecture, description))
        utcnow = datetime.utcnow()

        os = OperatingSystem(variant=variant,
                             version_number=version_number,
                             architecture=architecture,
                             description=description,
                             updated_by=user_id,
                             created=utcnow,
                             updated=utcnow)

        DBSession.add(os)
        DBSession.flush()
        return os
    except Exception as e:
        log.error('Error creating new operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
        raise


@view_config(route_name='api_operating_systems', request_method='GET', request_param='schema=true', renderer='json')
def api_operating_systems_schema(request):
    """Schema document for the operating_systems API."""

    os = {
    }

    return os


@view_config(route_name='api_operating_system_r', request_method='GET', renderer='json')
def api_operating_systemread_attrib(request):
    """Process read requests for the /api/operating_systems/{id}/{resource} route."""

    return get_api_attribute(request, 'OperatingSystem')


@view_config(route_name='api_operating_system', request_method='GET', renderer='json')
def api_operating_system_read_id(request):
    """Process read requests for the /api/operating_systems/{id} route."""

    return api_read_by_id(request, 'OperatingSystem')


@view_config(route_name='api_operating_systems', request_method='GET', renderer='json')
def api_operating_system_read(request):

    return api_read_by_params(request, 'OperatingSystem')


@view_config(route_name='api_operating_systems', permission='api_write', request_method='PUT', renderer='json')
def api_operating_system_write(request):
    """Process write requests for /api/operating_systems route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        variant = payload['variant']
        version_number = payload['version_number']
        architecture = payload['architecture']
        description = payload['description']

        log.info('Checking for operating_system variant={0},version_number={1},architecture={2}'.format(variant, version_number, architecture))
        try:
            os = DBSession.query(OperatingSystem)
            os = os.filter(OperatingSystem.variant==variant)
            os = os.filter(OperatingSystem.version_number==version_number)
            os = os.filter(OperatingSystem.architecture==architecture)
            os = os.one()
        except NoResultFound:
            os = create_operating_system(variant, version_number, architecture, description, au['user_id'])
        else:
            try:
                log.info('Updating operating_system variant={0},version_number={1},architecture={2},description={3}'.format(variant, version_number, architecture, description))

                os.variant = variant
                os.version_number = version_number
                os.architecture = architecture
                os.description = description
                os.updated_by=au['user_id']

                DBSession.flush()
            except Exception as e:
                log.error('Error updating operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
                raise

        return os

    except Exception as e:
        log.error('Error writing to operating_systems API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_operating_system', permission='api_write', request_method='DELETE', renderer='json')
def api_operating_systems_delete_id(request):
    """Process delete requests for the /api/operating_systems/{id} route."""

    return api_delete_by_id(request, 'OperatingSystem')


@view_config(route_name='api_operating_systems', permission='api_write', request_method='DELETE', renderer='json')
def api_operating_systems_delete(request):
    """Process delete requests for the /api/operating_systems route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'OperatingSystem')


