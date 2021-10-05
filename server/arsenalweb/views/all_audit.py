'''Arsenal audit UI.'''
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

@view_config(route_name='data_centers_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='hardware_profiles_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='ip_addresses_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='network_interfaces_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='node_groups_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='nodes_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='operating_systems_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='statuses_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
@view_config(route_name='tags_audit', permission='view', renderer='arsenalweb:templates/all_audit.pt')
def view_all_audit(request):
    '''Handle requests for the overall object type audit UI route.'''

    page_title_type = 'objects/'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    meta = {
        'data_centers_audit': {
            'page_type': 'Data Centers',
            'object_type': 'data_centers',
        },
        'hardware_profiles_audit': {
            'page_type': 'Hardware Profiles',
            'object_type': 'hardware_profiles',
        },
        'ip_addresses_audit': {
            'page_type': 'IpAddress',
            'object_type': 'ip_addresses',
        },
        'network_interfaces_audit': {
            'page_type': 'NetworkInterface',
            'object_type': 'network_interfaces',
        },
        'nodes_audit': {
            'page_type': 'Node',
            'object_type': 'nodes',
        },
        'node_groups_audit': {
            'page_type': 'Node Group',
            'object_type': 'node_groups',
        },
        'operating_systems_audit': {
            'page_type': 'Operating Systems',
            'object_type': 'operating_systems',
        },
        'statuses_audit': {
            'page_type': 'Status',
            'object_type': 'statuses',
        },
        'tags_audit': {
            'page_type': 'Tags',
            'object_type': 'tags',
        },
    }

    params = meta[request.matched_route.name]
    page_title_name = '{0}_audit'.format(params['object_type'])
    uri = '/api/{0}_audit'.format(params['object_type'])

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    objects_audit = []

    if resp:
        total = resp['meta']['total']
        objects_audit = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'field', 'pretty_name': 'Field'},
        {'name': 'new_value', 'pretty_name': 'New Value'},
        {'name': 'node_audit_id', 'pretty_name': 'Audit ID'},
        {'name': 'object_id', 'pretty_name': '{0} ID'.format(params['page_type'])},
        {'name': 'old_value', 'pretty_name': 'Old Value'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'objects_audit': objects_audit,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'params': params,
        'perpage': perpage,
        'total': total,
    }
