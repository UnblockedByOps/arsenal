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
from sqlalchemy.sql import func
from sqlalchemy import or_
from sqlalchemy import desc
from sqlalchemy.sql import label
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    log,
    )
from arsenalweb.models import (
    DBSession,
    )

@view_config(route_name='test3', permission='view', renderer='arsenalweb:templates/test3.pt')
@view_config(route_name='test3', permission='api_write', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='test3', permission='view', request_param='format=xml', renderer='xml')
def view_test3(request):
    page_title = 'test.'
    au = get_authenticated_user(request)

    params = {'format': None,
              'type': 'vir',
             }
    for p in params:
        try:
            params[p] = request.params[p]
        except:
            pass

    format = params['format']
    type = params['type']

    return {'layout': site_layout('max'),
            'page_title': page_title,
            'au': au,
           }

