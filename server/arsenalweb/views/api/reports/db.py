'''Arsenal API Db Reports.'''
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
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views.api.common import (
    api_200,
)
from arsenalweb.models.common import (
    DBSession,
    Base,
)

LOG = logging.getLogger(__name__)

@view_config(route_name='api_reports_db', request_method='GET', request_param='schema=true', renderer='json')
def api_reports_db_schema(request):
    '''Schema document for tags API'''

    tag = {
    }

    return tag

@view_config(route_name='api_reports_db', request_method='GET', renderer='json')
def api_reports_db_read(request):
    '''Process read requests for the /api/reports/db route.'''

    query = DBSession.execute("SHOW STATUS WHERE Variable_name IN ('wsrep_local_recv_que_avg', 'wsrep_connected', 'wsrep_cluster_conf_id', 'wsrep_cluster_state_uuid', 'wsrep_local_state_comment', 'wsrep_cluster_status', 'wsrep_cluster_size', 'wsrep_ready')")

    db_status = {}
    for row in query:
        db_status[row[0]] = row[1]

    row_counts = {}
    for my_table in Base.metadata.tables.keys():
        LOG.debug('Counting rows in table {0}'.format(my_table))
        table_count = DBSession.execute('SELECT COUNT(*) FROM {0}'.format(my_table))
        table_count = table_count.fetchone()
        row_counts[my_table] = table_count[0]
        LOG.debug('table: {0} count: {1}'.format(my_table, table_count[0]))

    db_status['row_counts'] = row_counts

    LOG.debug(db_status)

    return api_200(results=db_status)
