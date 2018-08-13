'''Arsenal API Node Reports.'''
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
import re
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views.api.common import (
    api_200,
)
from arsenalweb.models.common import (
    DBSession,
)
from arsenalweb.models.hardware_profiles import (
    HardwareProfile,
)
from arsenalweb.models.nodes import (
    Node,
)
from arsenalweb.models.operating_systems import (
    OperatingSystem,
)
from arsenalweb.models.statuses import (
    Status,
)

LOG = logging.getLogger(__name__)

def sanitize_input(input_string):
    '''Sanitize strings for use as graphite metrics.'''

    # FIXME: I'm sure this can be better
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    convert = a.sub(r'\1', input_string).lower().strip()
    convert = ' '.join(convert.split())
    convert = convert.replace(' ', '_')
    convert = convert.replace('-', '_')
    convert = convert.replace('.', '_')
    convert = convert.replace(',', '')
    convert = convert.replace('__', '_')
    convert = convert.replace('+', '_plus')
    convert = convert.replace('(', '')
    convert = convert.replace(')', '')

    return convert

@view_config(route_name='api_reports_nodes', request_method='GET', renderer='json')
def api_reports_node_read(request):
    '''Process read requests for the /api/reports/node route.'''

    node_metrics = {}
    try:
        LOG.debug('Generating metrics...')

        statuses = DBSession.query(Status)
        statuses = statuses.all()

        hw_profiles = DBSession.query(HardwareProfile)
        hw_profiles = hw_profiles.all()

        operating_systems = DBSession.query(OperatingSystem)
        operating_systems = operating_systems.all()

        node_metrics['status'] = {}
        for status in statuses:

            LOG.debug('Status id: {0}'.format(status.id))

            node = DBSession.query(Node)
            node = node.filter(Node.status_id == status.id)
            node_count = node.count()
            node_metrics['status'][status.name] = node_count

        node_metrics['operating_system'] = {}
        for operating_system in operating_systems:

            LOG.debug('Operating System id: {0}'.format(operating_system.id))

            node = DBSession.query(Node)
            node = node.filter(Node.operating_system_id == operating_system.id)
            node_count = node.count()
            os_name = sanitize_input('{0} {1}'.format(operating_system.variant,
                                                      operating_system.version_number))
            node_metrics['operating_system'][os_name] = node_count

        node_metrics['hardware_profile'] = {}
        for hw_profile in hw_profiles:

            LOG.debug('Hardware Profile id: {0}'.format(hw_profile.id))

            node = DBSession.query(Node)
            node = node.filter(Node.hardware_profile_id == hw_profile.id)
            node_count = node.count()
            hw_profile_name = sanitize_input('{0} {1}'.format(hw_profile.manufacturer,
                                                              hw_profile.model))
            node_metrics['hardware_profile'][hw_profile_name] = node_count

    except NoResultFound:
        LOG.error('This should never happen')

    LOG.debug('Metrics: {0}'.format(node_metrics))

    return api_200(results=node_metrics)
