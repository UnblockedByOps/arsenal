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
from arsenalweb.models.data_centers import (
    DataCenter,
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

        data_centers = request.dbsession.query(DataCenter)
        data_centers = data_centers.all()

        statuses = request.dbsession.query(Status)
        statuses = statuses.all()

        hw_profiles = request.dbsession.query(HardwareProfile)
        hw_profiles = hw_profiles.all()

        operating_systems = request.dbsession.query(OperatingSystem)
        operating_systems = operating_systems.all()

        for data_center in data_centers:
            LOG.debug("Working on data_center: %s", data_center.name)
            node_metrics[data_center.name] = {}
            nodes = request.dbsession.query(Node)
            nodes = nodes.filter(Node.data_center == data_center)
            nodes_count = nodes.count()
            node_metrics[data_center.name]['total'] = nodes_count
            LOG.debug("total nodes: %s", nodes_count)

            for status in statuses:
                LOG.debug("Working on status: %s", status.name)
                nodes_by_status = nodes.filter(Node.status_id == status.id)
                node_metrics[data_center.name][status.name] = {}
                node_metrics[data_center.name][status.name]['hardware_profile'] = {}
                node_metrics[data_center.name][status.name]['operating_system'] = {}
                node_metrics[data_center.name][status.name]['total'] = nodes_by_status.count()

                for hw_profile in hw_profiles:
                    LOG.debug("Working on hardware_profile: %s", hw_profile.name)
                    nodes_by_hw_profile = nodes.filter(Node.hardware_profile_id == hw_profile.id)
                    nodes_by_hw_profile = nodes_by_hw_profile.filter(Node.status_id == status.id)
                    my_hw_profile = sanitize_input(hw_profile.name)
                    node_metrics[data_center.name][status.name]['hardware_profile'][my_hw_profile] = {}
                    node_metrics[data_center.name][status.name]['hardware_profile'][my_hw_profile]['total'] = nodes_by_hw_profile.count()

                for os in operating_systems:
                    LOG.debug("Working on operating_system: %s", os.name)
                    nodes_by_os = nodes.filter(Node.operating_system_id == os.id)
                    nodes_by_os = nodes_by_os.filter(Node.status_id == status.id)
                    my_os = sanitize_input(os.name)
                    node_metrics[data_center.name][status.name]['operating_system'][my_os] = {}
                    node_metrics[data_center.name][status.name]['operating_system'][my_os]['total'] = nodes_by_os.count()

    except NoResultFound:
        LOG.error('This should never happen')

    LOG.debug('Metrics: %s', node_metrics)

    return api_200(results=node_metrics)
