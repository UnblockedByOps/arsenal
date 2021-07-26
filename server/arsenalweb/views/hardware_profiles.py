'''Arsenal hardware_profiles UI.'''
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


@view_config(route_name='hardware_profile', permission='view', renderer='arsenalweb:templates/hardware_profile.pt')
def view_hardware_profile(request):
    '''Handle requests for hardware_profile UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'hardware_profile'
    user = request.identity

    uri = '/api/hardware_profiles/{0}'.format(request.matchdict['id'])
    hardware_profile = _api_get(request, uri)

    return {
        'au': user,
        'hardware_profile': hardware_profile['results'][0],
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }

@view_config(route_name='hardware_profiles', permission='view', renderer='arsenalweb:templates/hardware_profiles.pt')
def view_hardware_profiles(request):
    '''Handle requests for hardware profiles UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'hardware_profiles'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/hardware_profiles'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    hardware_profiles = []

    if resp:
        total = resp['meta']['total']
        hardware_profiles = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'hardware_profile_id', 'pretty_name': 'Hardware Profile ID'},
        {'name': 'manufacturer', 'pretty_name': 'Manufacturer'},
        {'name': 'model', 'pretty_name': 'Model'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'hardware_profiles': hardware_profiles,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
