'''Arsenal healthcheck.'''
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
import os.path
from pyramid.view import view_config
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_503,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='healthcheck', request_method='GET', renderer='json')
def healthcheck(request):
    '''The loadbalancer healthcheck endpoint.'''

    settings = request.registry.settings

    if os.path.exists(settings['arsenal.healthcheck_file']):
        return api_200()
    else:
        return api_503()
