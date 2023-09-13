'''Arsenal groups UI'''
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


@view_config(route_name='group', permission='view', renderer='arsenalweb:templates/group.pt')
def view_group(request):
    '''Handle requests for group UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'group'
    user = request.identity

    uri = '/api/groups/{0}'.format(request.matchdict['id'])
    group = _api_get(request, uri)

    return {
        'au': user,
        'group': group['results'][0],
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }

@view_config(route_name='groups', permission='view', renderer='arsenalweb:templates/groups.pt')
def view_groups(request):
    '''Handle requests for groups UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'groups'
    user = request.identity
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/groups'
    LOG.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    groups = []

    if resp:
        total = resp['meta']['total']
        groups = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'name', 'pretty_name': 'Name'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'groups': groups,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'total': total,
    }
