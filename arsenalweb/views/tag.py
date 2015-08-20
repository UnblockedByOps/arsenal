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
    log,
    _api_get,
    )

@view_config(route_name='tag', permission='view', renderer='arsenalweb:templates/tag.pt')
def view_tag(request):
    page_title = 'Tag'
    au = get_authenticated_user(request)

    uri = '/api/tags/{0}'.format(request.matchdict['id'])
    tag = _api_get(request, uri)

    return {'page_title': page_title,
            'au': au,
            'tag': tag,
           }
