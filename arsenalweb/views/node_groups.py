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
    log,
    _api_get,
    )


@view_config(route_name='node_groups', permission='view', renderer='arsenalweb:templates/node_groups.pt')
def view_node_groups(request):
    page_title_type = 'objects/'
    page_title_name = 'node_groups'
    au = get_authenticated_user(request)

    uri = '/api/node_groups'
    node_groups = _api_get(request, uri)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [ {'name': 'node_group_id', 'pretty_name': 'Node Group ID' },
                         {'name': 'node_group_name', 'pretty_name': 'Node Group Name' },
                         {'name': 'description', 'pretty_name': 'Node Group Description' },
                         {'name': 'owner', 'pretty_name': 'Node Group Owner' },
                         {'name': 'updated_by', 'pretty_name': 'Updated By' },
                         {'name': 'updated', 'pretty_name': 'Date Updated' },
                         {'name': 'created', 'pretty_name': 'Date Created' },
    ]

    return {'layout': site_layout('max'),
            'page_title_type': page_title_type,
            'page_title_name': page_title_name,
            'au': au,
            'column_selectors': column_selectors,
            'node_groups': node_groups,
           }
