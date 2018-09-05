'''Arsenal API testing.'''
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
import json
from pyramid.view import view_config
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.views import (
    get_authenticated_user,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    collect_params,
    )
from arsenalweb.views.api.hardware_profiles import (
    get_hardware_profile,
    create_hardware_profile,
    )
from arsenalweb.views.api.operating_systems import (
    get_operating_system,
    create_operating_system,
    )
from arsenalweb.views.api.tags import (
    manage_tags,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='api_testing', request_method='GET', renderer='json')
@view_config(route_name='api_testing', request_method='PUT', renderer='json')
def api_node_schema(request):
    '''An endpoint for quick tests'''

#    my_ip = '10.255.251.24'
#    query = DBSession.query(NetworkInterface)
#    query = query.join(IpAddress)
#    query = query.filter(IpAddress.ip_address == my_ip)
#    resp = query.all()
#    LOG.debug('RESP IS: {0}'.format(resp))
#    return resp

    return []
