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
from pyramid.httpexceptions import HTTPFound
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    log,
    )
from arsenalweb.models import (
    DBSession,
    )


@view_config(route_name='search', permission='view', renderer='arsenalweb:templates/search.pt')
def view_home(request):

    au = get_authenticated_user(request)

    for key, value in request.POST.iteritems():
        log.info('{0}: {1}'.format(key,value))

    url_base = '/{0}?'.format(request.POST.get('object_type'))
    url_suffix = request.POST.get('search_terms')
    return_url = '{0}{1}'.format(url_base, url_suffix)

    log.info('Search url is: {0}'.format(return_url))

    return HTTPFound(return_url)
