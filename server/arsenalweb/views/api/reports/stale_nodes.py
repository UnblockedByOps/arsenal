'''Arsenal API Stale Node Reports.'''
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
from datetime import timedelta
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.models.common import (
    DBSession,
)
from arsenalweb.models.nodes import (
    Node,
)
from arsenalweb.models.statuses import (
    Status,
)
from arsenalweb.views.api.common import (
    api_200,
)

LOG = logging.getLogger(__name__)

@view_config(route_name='api_reports_stale_nodes', request_method='GET', renderer='json')
def api_reports_stale_node_read(request):
    '''Process read requests for the /api/reports/stale_nodes route.'''

    hours_past = int(request.GET.get('hours_past', 4))
    status = request.GET.get('status', 'inservice')
    statuses = status.split(',')

    try:
        LOG.info('Searching for nodes with last_registered grater than {0} '
                 'hours in the following statuses: {1}...'.format(hours_past,
                                                                  statuses))
        status_ids = []
        for status in statuses:
            my_status = DBSession.query(Status)
            my_status = my_status.filter(Status.name == status)
            my_status = my_status.one()
            status_ids.append(my_status.id)

        threshold = datetime.now() - timedelta(hours=hours_past)
        node = DBSession.query(Node)
        node = node.filter(Node.last_registered <= threshold)
        node = node.filter(Node.status_id.in_(status_ids))
        nodes = node.all()
        total = node.count()

    except NoResultFound:
        nodes = []

    LOG.info('Found {0} nodes with last_registered grater than {1} '
             'hours in the following statuses: {2}.'.format(total,
                                                            hours_past,
                                                            statuses))
    LOG.debug('Nodes: {0}'.format(nodes))

    return api_200(results=nodes, total=total, result_count=total)
