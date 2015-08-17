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
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    log,
    _api_get,
    )


@view_config(route_name='operating_systems', permission='view', renderer='arsenalweb:templates/operating_systems.pt')
def view_operating_systems(request):
    page_title_type = 'object_'
    page_title_name = 'Hardware Profiles'
    au = get_authenticated_user(request)

    uri = '/api/operating_systems'
    operating_systems = _api_get(request, uri)

    return {'layout': site_layout('max'),
            'page_title_type': page_title_type,
            'page_title_name': page_title_name,
            'au': au,
            'operating_systems': operating_systems,
           }

