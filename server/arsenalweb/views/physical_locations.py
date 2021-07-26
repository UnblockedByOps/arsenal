'''Arsenal physical_locations UI'''
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

GET_FIELDS = [
    'address_1',
    'address_2',
    'admin_area',
    'city',
    'contact_name',
    'country',
    'created',
    'name',
    'phone_number',
    'postal_code',
    'provider',
    'updated',
    'updated_by',
]
JOINED_GET_FIELDS = ','.join(GET_FIELDS)

@view_config(route_name='physical_location', permission='view', renderer='arsenalweb:templates/physical_location.pt')
def view_physical_location(request):
    '''Handle requests for physical_location UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_location'
    user = request.identity

    params = {
        'fields': JOINED_GET_FIELDS + ',physical_racks'
    }

    uri = '/api/physical_locations/{0}'.format(request.matchdict['id'])
    physical_location = _api_get(request, uri, params)

    return {
        'au': user,
        'physical_location': physical_location['results'][0],
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }

@view_config(route_name='physical_locations', permission='view', renderer='arsenalweb:templates/physical_locations.pt')
def view_physical_locations(request):
    '''Handle requests for physical_locations UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_locations'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage
    payload['fields'] = JOINED_GET_FIELDS

    uri = '/api/physical_locations'
    LOG.debug('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    physical_locations = []

    if resp:
        total = resp['meta']['total']
        physical_locations = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'contact_name', 'pretty_name': 'DC Contact'},
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'name', 'pretty_name': 'Name'},
        {'name': 'phone_number', 'pretty_name': 'DC Phone Number'},
        {'name': 'provider', 'pretty_name': 'DC Provider'},
        {'name': 'address_1', 'pretty_name': 'Address 1'},
        {'name': 'address_2', 'pretty_name': 'Address 2'},
        {'name': 'city', 'pretty_name': 'City'},
        {'name': 'admin_area', 'pretty_name': 'State'},
        {'name': 'postal_code', 'pretty_name': 'Postal Code'},
        {'name': 'country', 'pretty_name': 'Country'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'physical_locations': physical_locations,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
