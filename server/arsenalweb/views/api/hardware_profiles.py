'''Arsenal API hardware_profiles.'''
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
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.hardware_profiles import (
    HardwareProfile,
    HardwareProfileAudit,
    )
from arsenalweb.views import (
    get_authenticated_user,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_500,
    )

LOG = logging.getLogger(__name__)


def get_hardware_profile(name):
    '''Get a hardware_profile from the database.'''

    try:
        query = DBSession.query(HardwareProfile)
        query = query.filter(HardwareProfile.name == name)
        hardware_profile = query.one()

        return hardware_profile

    except (NoResultFound, AttributeError):
        LOG.debug('hardware_profile not found name={0},'.format(name))

    return None

def create_hardware_profile(name, manufacturer, model, user_id):
    '''Create a new hardware_profile.'''

    try:
        LOG.info('Creating new hardware_profile name={0},manufacturer={1},'
                 'model={2}'.format(name, manufacturer, model))
        utcnow = datetime.utcnow()

        hardware_profile = HardwareProfile(name=name,
                                           manufacturer=manufacturer,
                                           model=model,
                                           rack_u=1,
                                           rack_color='#fff',
                                           updated_by=user_id,
                                           created=utcnow,
                                           updated=utcnow)

        DBSession.add(hardware_profile)
        DBSession.flush()

        audit = HardwareProfileAudit(object_id=hardware_profile.id,
                                     field='name',
                                     old_value='created',
                                     new_value=hardware_profile.name,
                                     updated_by=user_id,
                                     created=utcnow)
        DBSession.add(audit)
        DBSession.flush()

        return hardware_profile

    except Exception as ex:
        LOG.error('Error creating new harware_profile name={1},manufacturer={2},'
                  'model={3},exception={4}'.format(name, manufacturer, model, ex))
        raise

def update_hardware_profile(hardware_profile, name, rack_color, rack_u, user_id):
    '''Update an existing hardware_profile. We only allow updating rack_color and
    rack_u. All other hardware profile attributes are derived
    automatically during node registration.'''

    try:
        LOG.info('Updating hardware_profile name={0} rack_color={1} '
                 'rack_u={2}'.format(name, rack_color, rack_u))

        utcnow = datetime.utcnow()

        for attribute in ['rack_color', 'rack_u']:
            if getattr(hardware_profile, attribute) != locals()[attribute]:
                LOG.debug('Updating hardware profile {0}: {1}'.format(attribute,
                                                                      locals()[attribute]))
                audit = HardwareProfileAudit(object_id=hardware_profile.id,
                                             field=attribute,
                                             old_value=getattr(hardware_profile, attribute),
                                             new_value=locals()[attribute],
                                             updated_by=user_id,
                                             created=utcnow)
                DBSession.add(audit)

        hardware_profile.rack_color = rack_color
        hardware_profile.rack_u = rack_u
        hardware_profile.updated_by = user_id

        DBSession.flush()

        return hardware_profile

    except Exception as ex:
        LOG.error('Error updating hardware_profile name={0},rack_color={1},'
                  'rack_u={2},exception={3}'.format(name, rack_color, rack_u, ex))
        raise

@view_config(route_name='api_hardware_profiles', request_method='GET', request_param='schema=true', renderer='json')
def api_hardware_profiles_schema(request):
    '''Schema document for the hardware_profiles API.'''

    hardware_profile = {
        'id': 'Integer',
        'name': 'String',
        'model': 'String',
        'manufacturer': 'String',
        'created': 'Timestamp',
        'updated': 'Timestamp',
        'updated_by': 'String',
    }

    return hardware_profile

@view_config(route_name='api_hardware_profiles', permission='api_write', request_method='PUT', renderer='json')
def api_hardware_profile_write(request):
    '''Process write requests for /api/hardware_profiles route.'''

    try:
        auth_user = get_authenticated_user(request)
        payload = request.json_body
        name = payload['name'].rstrip()
        manufacturer = payload['manufacturer'].rstrip()
        model = payload['model'].rstrip()
        rack_u = payload['rack_u']
        rack_color = payload['rack_color'].rstrip()

        hardware_profile = get_hardware_profile(name)

        if not hardware_profile:
            hardware_profile = create_hardware_profile(name,
                                                       manufacturer,
                                                       model,
                                                       auth_user['user_id'])
        else:

            update_hardware_profile(hardware_profile,
                                    name,
                                    rack_color,
                                    rack_u,
                                    auth_user['user_id'])

        LOG.debug('hardware_profile is: {0}'.format(hardware_profile.__dict__))

        return api_200(results=hardware_profile)

    except Exception as ex:
        msg = 'Error writing to harware_profiles API={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)
