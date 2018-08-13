'''Arsenal tags UI.'''
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


@view_config(route_name='tag', permission='view', renderer='arsenalweb:templates/tag.pt')
def view_tag(request):
    '''Handle requests for tag UI route.'''

    page_title = 'Tag'
    auth_user = get_authenticated_user(request)

    uri = '/api/tags/{0}'.format(request.matchdict['id'])
    tag = _api_get(request, uri)

    return {
        'au': auth_user,
        'page_title': page_title,
        'tag': tag['results'][0],
    }

@view_config(route_name='tags', permission='view', renderer='arsenalweb:templates/tags.pt')
def view_tags(request):
    '''Handle requests for tags UI route.'''

    page_title_type = 'objects/'
    page_title_name = 'tags'
    auth_user = get_authenticated_user(request)
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    # Force the UI to 50 results per page
    if not perpage:
        perpage = 50

    payload['perpage'] = perpage

    uri = '/api/tags'
    LOG.info('UI requesting data from uri: {0} payload: {1}'.format(uri, payload))

    resp = _api_get(request, uri, payload)

    total = 0
    tags = []

    if resp:
        total = resp['meta']['total']
        tags = resp['results']

    nav_urls = get_nav_urls(request.path, offset, perpage, total, payload)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'tag_id', 'pretty_name': 'Tag ID'},
        {'name': 'tag_name', 'pretty_name': 'Tag Name'},
        {'name': 'tag_value', 'pretty_name': 'Tag Value'},
        {'name': 'updated', 'pretty_name': 'Date Updated'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': auth_user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'nav_urls': nav_urls,
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'tags': tags,
        'total': total,
    }
