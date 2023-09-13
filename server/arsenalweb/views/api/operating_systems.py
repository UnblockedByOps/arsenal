'''Arsenal API OperatingSystems.'''
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
    api_500,
    )
from arsenalweb.models.operating_systems import (
    OperatingSystem,
    OperatingSystemAudit,
    )

LOG = logging.getLogger(__name__)


# Common functions
def get_operating_system(dbsession, name):
    '''Get an operating_system from the database.'''

    try:
        query = dbsession.query(OperatingSystem)
        query = query.filter(OperatingSystem.name == name)
        operating_system = query.one()

        return operating_system

    except (NoResultFound, AttributeError):
        LOG.debug('operating_system not found name: %s', name)

    return None

def create_operating_system(dbsession, name, variant, version_number, architecture, description, user_id):
    '''Create a new operating_system.'''

    try:
        LOG.info('Creating new operating_system name: %s variant: %s version_number: %s '
                 'architecture: %s description: %s', name,
                                                     variant,
                                                     version_number,
                                                     architecture,
                                                     description)
        utcnow = datetime.utcnow()

        operating_system = OperatingSystem(name=name,
                                           variant=variant,
                                           version_number=version_number,
                                           architecture=architecture,
                                           description=description,
                                           updated_by=user_id,
                                           created=utcnow,
                                           updated=utcnow)
        dbsession.add(operating_system)
        dbsession.flush()

        audit = OperatingSystemAudit(object_id=operating_system.id,
                                     field='name',
                                     old_value='created',
                                     new_value=operating_system.name,
                                     updated_by=user_id,
                                     created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return operating_system

    except Exception as ex:
        msg = 'Error creating new operating_system name: {0} variant: {1} version_number: {2} ' \
              'architecture: {3} description: {4} exception: {5}'.format(name,
                                                                         variant,
                                                                         version_number,
                                                                         architecture,
                                                                         description,
                                                                         ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_operating_system(dbsession,
                            operating_system,
                            name,
                            variant,
                            version_number,
                            architecture,
                            description,
                            user_id):
    '''Update an existing operating_system.'''

    try:
        LOG.info('Updating operating_system name: %s variant: %s version_number: %s '
                 'architecture: %s description: %s', name,
                                                     variant,
                                                     version_number,
                                                     architecture,
                                                     description)

        utcnow = datetime.utcnow()

        for attribute in ['name',
                          'variant',
                          'version_number',
                          'architecture',
                          'description']:
            if getattr(operating_system, attribute) != locals()[attribute]:
                LOG.debug('Updating operating system %s: %s', attribute, locals()[attribute])
                audit = OperatingSystemAudit(object_id=operating_system.id,
                                             field=attribute,
                                             old_value=getattr(operating_system, attribute),
                                             new_value=locals()[attribute],
                                             updated_by=user_id,
                                             created=utcnow)
                dbsession.add(audit)

        operating_system.name = name
        operating_system.variant = variant
        operating_system.version_number = version_number
        operating_system.architecture = architecture
        operating_system.description = description
        operating_system.updated_by = user_id

        dbsession.flush()

        return operating_system

    except Exception as ex:
        msg = 'Error updating operating_system name: {0} variant: {1} version_number: {2} ' \
              'architecture: {3} description: {4} exception: {5}'.format(name,
                                                                         variant,
                                                                         version_number,
                                                                         architecture,
                                                                         description,
                                                                         ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_operating_systems', request_method='GET', request_param='schema=true', renderer='json')
def api_operating_systems_schema(request):
    '''Schema document for the operating_systems API.'''

    operating_system = {
    }

    return operating_system

@view_config(route_name='api_operating_systems', permission='api_write', request_method='PUT', renderer='json', require_csrf=False)
def api_operating_system_write(request):
    '''Process write requests for /api/operating_systems route.'''

    try:
        user = request.identity
        payload = request.json_body

        name = payload['name'].rstrip()
        variant = payload['variant'].rstrip()
        version_number = payload['version_number'].rstrip()
        architecture = payload['architecture'].rstrip()
        description = payload['description'].rstrip()

        operating_system = get_operating_system(request.dbsession, name)

        if not operating_system:
            operating_system = create_operating_system(request.dbsession,
                                                       name,
                                                       variant,
                                                       version_number,
                                                       architecture,
                                                       description,
                                                       user['name'])
        else:
            operating_system = update_operating_system(request.dbsession,
                                                       operating_system,
                                                       name,
                                                       variant,
                                                       version_number,
                                                       architecture,
                                                       description,
                                                       user['name'])

        return operating_system

    except Exception as ex:
        msg = 'Error writing to operating_systems API: {0} ' \
              'exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)
