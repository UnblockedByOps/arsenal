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
from datetime import timedelta
import arrow
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    log,
    _api_get,
    )
from arsenalweb.models import (
    DBSession,
    User,
    )


@view_config(route_name='nodes', permission='view', renderer='arsenalweb:templates/nodes.pt')
def view_nodes(request):
    page_title = 'Nodes'
    au = get_authenticated_user(request)

    params = {'type': 'vir',
             }
    for p in params:
        try:
            params[p] = request.params[p]
        except:
            pass

    uri = '/api/nodes'
    nodes = _api_get(request, uri)

    return {'layout': site_layout('max'),
            'page_title': page_title,
            'au': au,
            'nodes': nodes,
           }
