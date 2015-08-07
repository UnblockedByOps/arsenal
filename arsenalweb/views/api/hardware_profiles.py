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
from arsenalweb.models import (
    DBSession,
    HardwareProfile,
    )

@view_config(route_name='api_hardware_profiles', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profiles', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_hardware_profile', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profile', request_method='GET', request_param='format=json', renderer='json')
def api_hardware_profile_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        if request.path == '/api/hardware_profiles':

            model = request.params.get('model')
            manufacturer = request.params.get('manufacturer')

            if model:
                log.info('Querying for hardware_profile: {0}'.format(request.url))
                try:
                    q = DBSession.query(HardwareProfile)
                    q = q.filter(HardwareProfile.manufacturer==manufacturer)
                    q = q.filter(HardwareProfile.model==model)
                    return q.one()
                except NoResultFound:
                    return Response(content_type='application/json', status_int=404)
                except Exception, e:
                    log.error('Error querying hardware_profile={0},exception={2}'.format(request.url, e))
                    raise

            else:
                log.info('Displaying all hardware profiles')
                try:
                    q = DBSession.query(HardwareProfile)
                    return q.limit(perpage).offset(offset).all()
                except NoResultFound:
                    return Response(content_type='application/json', status_int=404)
                except Exception, e:
                    log.error('Error querying for hardware_profiles={0},exception={0}'.format(request.url, e))
                    raise

        if request.matchdict['id']:
            log.info('Displaying single hardware profile')
            try:
                q = DBSession.query(HardwareProfile)
                q = q.filter(HardwareProfile.hardware_profile_id==request.matchdict['id'])
                return q.one()
            except NoResultFound:
                return Response(content_type='application/json', status_int=404)
            except Exception, e:
                log.error('Error querying for hardware_profile={0},exception={1}'.format(request.url, e))
                raise
            
    except Exception, e:
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_hardware_profiles', permission='api_write', request_method='PUT', renderer='json')
def api_hardware_profile_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body
        manufacturer = payload['manufacturer']
        model = payload['model']

        if request.path == '/api/hardware_profiles':

            log.info('Checking for hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))
            try:
                q = DBSession.query(HardwareProfile)
                q = q.filter(HardwareProfile.manufacturer==manufacturer)
                q = q.filter(HardwareProfile.model==model)
                q.one()
            except NoResultFound, e:
                try:
                    log.info('Creating new hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))
                    utcnow = datetime.utcnow()
                    hp = HardwareProfile(manufacturer = manufacturer,
                                         model = model,
                                         updated_by = au['user_id'],
                                         created = utcnow,
                                         updated = utcnow)
                    DBSession.add(hp)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error creating new harware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
                    raise
            # Update
            else:
                try:
                    log.info('Updating hardware_profile manufacturer={0},model={1}'.format(manufacturer, model))

                    hp = DBSession.query(HardwareProfile)
                    hp = hp.filter(HardwareProfile.manufacturer==manufacturer)
                    hp = hp.filter(HardwareProfile.model==model)
                    hp = hp.one()

                    hp.manufacturer = manufacturer
                    hp.model = model
                    hp.updated_by=au['user_id']

                    DBSession.flush()
                except Exception, e:
                    log.error('Error updating hardware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
                    raise

            return hp

    except Exception, e:
        return Response(str(e), content_type='text/plain', status_int=500)
