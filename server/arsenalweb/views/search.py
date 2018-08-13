'''Arsenal search UI.'''
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
from pyramid.httpexceptions import HTTPFound

LOG = logging.getLogger(__name__)

@view_config(route_name='search', permission='view', renderer='arsenalweb:templates/search.pt')
def view_home(request):
    '''Handle requests for search UI route.'''

    for key, value in request.POST.iteritems():
        LOG.debug('Searching for {0}: {1}'.format(key, value))

    url_base = '/{0}?'.format(request.POST.get('object_type'))
    search_params = request.POST.get('search_terms')
    url_suffix = ''
    for term in search_params.split():
        if '=' not in term:
            key = 'name'
            val = term
        else:
            key, val = term.split('=')

        url_suffix += '{0}={1}&'.format(key, val)
    url_suffix = url_suffix[:-1]

    return_url = '{0}{1}'.format(url_base, url_suffix)

    LOG.debug('Search url is: {0}'.format(return_url))

    return HTTPFound(return_url)
