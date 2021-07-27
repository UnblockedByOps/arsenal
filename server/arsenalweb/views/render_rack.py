'''Arsenal render_rack UI'''
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
import json
from pyramid.view import view_config
from arsenalweb.views import (
    _api_get,
    get_nav_urls,
    get_pag_params,
    site_layout,
    )

LOG = logging.getLogger(__name__)


def get_empty_rack(elevation):
    '''Returns an empty physical_device object populated with an elevation.
    This is so empty elevations have all the required attributes to render in
    the UI correctly.'''

    LOG.debug('Creating dummy elevation for elevation: {0}'.format(elevation))

    device = {
        'physical_elevation': {
            'elevation': elevation,
        },
        'hardware_profile': {
            'id': 0,
            'name': 'N/A',
            'rack_u': 1,
            'rack_color': '#fff',
        },
        'node': {},
        'id': 0,
        'serial_number': 'N/A',
        'oob_ip_address': 'N/A',
        'status': {
            'name': 'N/A',
        }
    }

    return device

@view_config(route_name='render_rack', permission='view', renderer='arsenalweb:templates/render_rack.pt')
def view_render_rack(request):
    '''Handle requests for render_rack UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'render_rack'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    payload['perpage'] = perpage
    location_name = request.params['physical_location.name']
    rack_name = request.params['physical_rack.name']

    uri = '/api/physical_racks'
    pr_payload = {
        'name': rack_name,
        'physical_location.name': location_name,
        'fields': 'all',
    }
    LOG.debug('UI requesting data from API: %s payload: %s', uri, pr_payload)

    pr_resp = _api_get(request, uri, pr_payload)
    my_rack_elevations = pr_resp['results'][0]['physical_elevations']

    uri = '/api/physical_devices'
    LOG.debug('UI requesting data from API: %s payload: %s', uri, payload)

    pd_resp = _api_get(request, uri, payload)
    my_physical_devices = pd_resp['results']

    physical_devices = []

    if pd_resp:
        for elevation in my_rack_elevations:
            if not elevation['physical_device']:
                empty_rack = get_empty_rack(elevation['elevation'])
                my_physical_devices.append(empty_rack)

        for pde in my_physical_devices:
            try:
                pde['hardware_profile']['rack_u_pxl'] = pde['hardware_profile']['rack_u'] * 120
            # hardware_profile doesn't have rack_u set, set to 1
            except TypeError:
                pde['hardware_profile']['rack_u'] = 1
                pde['hardware_profile']['rack_u_pxl'] = 120

        try:
            physical_devices = sorted(my_physical_devices, key=lambda k: int(k['physical_elevation']['elevation']), reverse=True)
        except ValueError:
            physical_devices = sorted(my_physical_devices, key=lambda k: k['physical_elevation']['elevation'], reverse=True)

        # Remove rack elevations occupied by a device greater than 1 U
        for device in physical_devices:
            if device['hardware_profile']['rack_u'] > 1:
                # Get the list of u to be deleted
                start = int(device['physical_elevation']['elevation']) + 1
                end = start + device['hardware_profile']['rack_u'] - 1
                for delete_me in range(start, end):
                    LOG.debug('Delete physical_elevation from the list: %s', delete_me)
                    physical_devices = [i for i in physical_devices if not (int(i['physical_elevation']['elevation']) == delete_me)]

#        LOG.debug(json.dumps(physical_devices, indent=4, sort_keys=True))

    return {
        'au': user,
        'layout': site_layout('max'),
        'location_name': location_name,
        'rack_name': rack_name,
        'physical_devices': physical_devices,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }
