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
    OperatingSystem,
    )

@view_config(route_name='api_operating_systems', request_method='GET', renderer='json')
@view_config(route_name='api_operating_systems', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_operating_systems', request_method='GET', request_param='format=xml', renderer='xml')
@view_config(route_name='api_operating_system', request_method='GET', renderer='json')
@view_config(route_name='api_operating_system', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_operating_system', request_method='GET', request_param='format=xml', renderer='xml')
def api_operating_system_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        if request.path == '/api/operating_systems':

            variant = request.params.get('variant')
            version_number = request.params.get('version_number')
            architecture = request.params.get('architecture')

            if variant:
                log.info('Querying for operating_system: {0}'.format(request.url))
                try:
                    q = DBSession.query(OperatingSystem)
                    q = q.filter(OperatingSystem.variant==variant)
                    q = q.filter(OperatingSystem.version_number==version_number)
                    q = q.filter(OperatingSystem.architecture==architecture)
                    return q.one()
                except Exception, e:
                    log.error('Error querying operating_system={0},exception={2}'.format(request.url, e))
                    raise

            else:
                log.info('Displaying all operating systems')
                try:
                    q = DBSession.query(OperatingSystem)
                    return q.limit(perpage).offset(offset).all()
                except Exception, e:
                    log.error('Error querying for operating_systems={0},exception={0}'.format(request.url, e))
                    raise

        if request.matchdict['id']:
            log.info('Displaying single operating system')
            try:
                q = DBSession.query(OperatingSystem)
                q = q.filter(OperatingSystem.operating_system_id==request.matchdict['id'])
                return q.one()
            except Exception, e:
                log.error('Error querying for operating_system={0},exception={1}'.format(request.url, e))
                raise
            
    except NoResultFound:
        return Response(content_type='application/json', status_int=404)
    except Exception, e:
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_operating_systems', permission='api_write', request_method='PUT', renderer='json')
def api_operating_system_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body
        variant = payload['variant']
        version_number = payload['version_number']
        architecture = payload['architecture']
        description = payload['description']

        if request.path == '/api/operating_systems':

            log.info('Checking for operating_system variant={0},version_number={1},architecture={2}'.format(variant, version_number, architecture))
            try:
                q = DBSession.query(OperatingSystem)
                q = q.filter(OperatingSystem.variant==variant)
                q = q.filter(OperatingSystem.version_number==version_number)
                q = q.filter(OperatingSystem.architecture==architecture)
                os = q.one()
            except NoResultFound, e:
                try:
                    log.info('Creating new operating_system variant={0},version_number={1},architecture={2},description={3}'.format(variant, version_number, architecture, description))
                    utcnow = datetime.utcnow()
                    os = OperatingSystem(variant=variant,
                                         version_number=version_number,
                                         architecture=architecture,
                                         description=description,
                                         updated_by=au['user_id'],
                                         created=utcnow,
                                         updated=utcnow)
                    DBSession.add(os)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error creating new operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
                    raise
            # Update
            else:
                try:
                    log.info('Updating operating_system variant={0},version_number={1},architecture={2},description={3}'.format(variant, version_number, architecture, description))

                    os.variant = variant
                    os.version_number = version_number
                    os.architecture = architecture
                    os.description = description
                    os.updated_by=au['user_id']

                    DBSession.flush()
                except Exception, e:
                    log.error('Error updating operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
                    raise

            return os

    except Exception, e:
        return Response(str(e), content_type='text/plain', status_int=500)
