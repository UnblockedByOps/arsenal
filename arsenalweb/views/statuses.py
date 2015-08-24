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
from pyramid.view import view_config
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    get_pag_params,
    log,
    _api_get,
    )


@view_config(route_name='statuses', permission='view', renderer='arsenalweb:templates/statuses.pt')
def view_statuses(request):

    page_title_type = 'objects/'
    page_title_name = 'statuses'
    au = get_authenticated_user(request)
    (perpage, offset) = get_pag_params(request)

    payload = {}
    for k in request.GET:
        payload[k] = request.GET[k]

    uri = '/api/statuses'
    log.info('UI requesting data from API={0},payload={1}'.format(uri, payload))

    if payload:
        r = _api_get(request, uri, payload)
    else:
        r = _api_get(request, uri)

    if r:
        total = r['meta']['total']
        statuses = r['results']
    else:
        total = 0
        statuses = []

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [ {'name': 'status_id', 'pretty_name': 'Status ID' },
                         {'name': 'status_name', 'pretty_name': 'Status Name' },
                         {'name': 'description', 'pretty_name': 'Description' },
                         {'name': 'updated_by', 'pretty_name': 'Updated By' },
                         {'name': 'updated', 'pretty_name': 'Date Updated' },
                         {'name': 'created', 'pretty_name': 'Date Created' },
    ]

    return {'layout': site_layout('max'),
            'page_title_type': page_title_type,
            'page_title_name': page_title_name,
            'offset': offset,
            'perpage': perpage,
            'total': total,
            'au': au,
            'column_selectors': column_selectors,
            'statuses': statuses,
           }
