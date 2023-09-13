'''Arsenal operating_systems UI.'''
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
from arsenalweb.views import (
    _api_get,
    get_nav_urls,
    get_pag_params,
    site_layout,
    )

LOG = logging.getLogger(__name__)


@view_config(route_name='operating_system', permission='view', renderer='arsenalweb:templates/operating_system.pt')
def view_operating_system(request):
    '''Handle requests for opaerating_system UI route.'''

    page_title = 'Operating System'
    user = request.identity

    uri = '/api/operating_systems/{0}'.format(request.matchdict['id'])
    operating_system = _api_get(request, uri)

    return {
        'au': user,
        'operating_system': operating_system['results'][0],
        'page_title': page_title,
    }

@view_config(route_name='operating_systems', permission='view', renderer='arsenalweb:templates/operating_systems.pt')
def view_operating_systems(request):
    '''Handle requests for operating_systems UI route.'''

    page_title_type = 'object/'
    page_title_name = 'operating_systems'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/operating_systems'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    operating_systems = []

    if resp:
        total = resp['meta']['total']
        operating_systems = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'architecture', 'pretty_name': 'Architecture'},
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'description', 'pretty_name': 'Description'},
        {'name': 'operating_system_id', 'pretty_name': 'Operating system ID'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
        {'name': 'variant', 'pretty_name': 'Variant'},
        {'name': 'version_number', 'pretty_name': 'Version Number'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'offset': offset,
        'operating_systems': operating_systems,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
