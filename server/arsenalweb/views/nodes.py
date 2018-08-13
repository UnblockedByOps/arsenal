'''Arsenal nodes UI.'''
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


@view_config(route_name='node', permission='view', renderer='arsenalweb:templates/node.pt')
def view_node(request):
    '''Handle requests for node UI route.'''

    page_title = 'Node'
    auth_user = get_authenticated_user(request)

    uri = '/api/nodes/{0}'.format(request.matchdict['id'])
    resp = _api_get(request, uri)
    node = resp['results'][0]

    # We need all the info about network_interfaces for display in the UI.
    net_ifs = []
    for net_if in node['network_interfaces']:
        LOG.info('Getting network interface: {0}'.format(net_if))
        uri = '/api/network_interfaces/{0}'.format(net_if['id'])
        resp = _api_get(request, uri)
        net_ifs.append(resp['results'][0])
    node['network_interfaces'] = sorted(net_ifs, key=lambda k: k['name'])

    LOG.debug('network interfaces: {0}'.format(node['network_interfaces']))

    return {
        'au': auth_user,
        'node': node,
        'page_title': page_title,
    }

@view_config(route_name='nodes', permission='view', renderer='arsenalweb:templates/nodes.pt')
def view_nodes(request):
    '''Handle requests for nodes UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'nodes'
    auth_user = get_authenticated_user(request)
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/nodes'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    nodes = []

    if resp:
        total = resp['meta']['total']
        nodes = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'hardware_profile', 'pretty_name': 'Hardware Profile'},
        {'name': 'last_registered', 'pretty_name': 'Last Registered'},
        {'name': 'node_groups', 'pretty_name': 'Node Groups'},
        {'name': 'node_id', 'pretty_name': 'Node ID'},
        {'name': 'node_name', 'pretty_name': 'Node Name'},
        {'name': 'operating_system', 'pretty_name': 'Operating System'},
        {'name': 'status', 'pretty_name': 'Status'},
        {'name': 'unique_id', 'pretty_name': 'Unique ID'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': auth_user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'nodes': nodes,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
