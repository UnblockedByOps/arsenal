'''Arsenal physical_racks UI'''
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
    get_authenticated_user,
    get_nav_urls,
    get_pag_params,
    site_layout,
    )

LOG = logging.getLogger(__name__)


@view_config(route_name='physical_rack', permission='view', renderer='arsenalweb:templates/physical_rack.pt')
def view_physical_rack(request):
    '''Handle requests for physical_rack UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_rack'
    auth_user = get_authenticated_user(request)

    uri = '/api/physical_racks/{0}'.format(request.matchdict['id'])
    physical_rack = _api_get(request, uri)

    return {
        'au': auth_user,
        'physical_rack': physical_rack['results'][0],
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }

@view_config(route_name='physical_racks', permission='view', renderer='arsenalweb:templates/physical_racks.pt')
def view_physical_racks(request):
    '''Handle requests for physical_racks UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_racks'
    auth_user = get_authenticated_user(request)
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/physical_racks'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    physical_racks = []

    if resp:
        total = resp['meta']['total']
        physical_racks = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'name', 'pretty_name': 'Name'},
        {'name': 'physical_location', 'pretty_name': 'Physical Location'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': auth_user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'physical_racks': physical_racks,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
