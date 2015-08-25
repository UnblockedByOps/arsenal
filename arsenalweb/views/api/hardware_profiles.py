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
    get_pag_params,
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
    HardwareProfile,
    )


def create_hardware_profile(manufacturer, model, user_id):
    """Create a new hardware_profile."""

    try:
        log.info('Creating new hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))
        utcnow = datetime.utcnow()

        hp = HardwareProfile(manufacturer = manufacturer,
                             model = model,
                             updated_by = user_id,
                             created = utcnow,
                             updated = utcnow)

        DBSession.add(hp)
        DBSession.flush()
        return hp
    except Exception as e:
        log.error('Error creating new harware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
        raise


@view_config(route_name='api_hardware_profiles', request_method='GET', request_param='schema=true', renderer='json')
def api_hardware_profiles_schema(request):
    """Schema document for the hardware_profiles API."""

    hp = {
    }

    return hp


@view_config(route_name='api_hardware_profile_r', request_method='GET', renderer='json')
def api_hardware_profile_read_attrib(request):
    """Process read requests for the /api/hardware_profiles/{id}/{resource} route."""

    return get_api_attribute(request, 'HardwareProfile')


@view_config(route_name='api_hardware_profile', request_method='GET', renderer='json')
def api_hardware_profile_read_id(request):
    """Process read requests for the /api/node_groups/{id} route."""

    return api_read_by_id(request, 'HardwareProfile')


@view_config(route_name='api_hardware_profiles', request_method='GET', renderer='json')
def api_hardware_profile_read(request):
    """Process read requests for the /api/hardware_profiles route."""

    return api_read_by_params(request, 'HardwareProfile')


@view_config(route_name='api_hardware_profiles', permission='api_write', request_method='PUT', renderer='json')
def api_hardware_profile_write(request):
    """Process write requests for /api/hardware_profiles route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        manufacturer = payload['manufacturer']
        model = payload['model']

        log.debug('Checking for hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))

        try:
            hp = DBSession.query(HardwareProfile)
            hp = hp.filter(HardwareProfile.manufacturer==manufacturer)
            hp = hp.filter(HardwareProfile.model==model)
            hp = hp.one()
        except NoResultFound:
            hp = create_hardware_profile(manufacturer, model, au['user_id'])
        else:
            try:
                log.info('Updating hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))

                hp.manufacturer = manufacturer
                hp.model = model
                hp.updated_by=au['user_id']

                DBSession.flush()
            except Exception as e:
                log.error('Error updating hardware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
                raise

        return hp

    except Exception as e:
        log.error('Error writing to harware_profiles API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_hardware_profile', permission='api_write', request_method='DELETE', renderer='json')
def api_hardware_profiles_delete_id(request):
    """Process delete requests for the /api/hardware_profiles/{id} route."""

    return api_delete_by_id(request, 'HardwareProfile')


@view_config(route_name='api_hardware_profiles', permission='api_write', request_method='DELETE', renderer='json')
def api_hardware_profiles_delete(request):
    """Process delete requests for the /api/hardware_profiles route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'HardwareProfile')


