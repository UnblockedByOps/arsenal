'''Arsenal physical_devices UI'''
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


@view_config(route_name='physical_device', permission='view', renderer='arsenalweb:templates/physical_device.pt')
def view_physical_device(request):
    '''Handle requests for physical_device UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_device'
    user = request.identity

    uri = '/api/physical_devices/{0}'.format(request.matchdict['id'])
    physical_device = _api_get(request, uri)

    return {
        'au': user,
        'physical_device': physical_device['results'][0],
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }

@view_config(route_name='physical_devices', permission='view', renderer='arsenalweb:templates/physical_devices.pt')
def view_physical_devices(request):
    '''Handle requests for physical_devices UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'physical_devices'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/physical_devices'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    physical_devices = []

    if resp:
        total = resp['meta']['total']
        physical_devices = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'hardware_profile', 'pretty_name': 'Hardware Profile'},
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'mac_address_1', 'pretty_name': 'Mac Address 1'},
        {'name': 'mac_address_2', 'pretty_name': 'Mac Address 2'},
        {'name': 'oob_ip_address', 'pretty_name': 'OOB IP Address'},
        {'name': 'oob_mac_address', 'pretty_name': 'OOB Mac Address'},
        {'name': 'received_date', 'pretty_name': 'Received Date'},
        {'name': 'inservice_date', 'pretty_name': 'Inservice Date'},
        {'name': 'physical_location', 'pretty_name': 'Physical Location'},
        {'name': 'physical_elevation', 'pretty_name': 'Physical Elevation'},
        {'name': 'physical_rack', 'pretty_name': 'Physical Rack'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'physical_devices': physical_devices,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
