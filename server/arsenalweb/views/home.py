'''Arsenal home UI.'''
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
from pyramid.response import Response
from datetime import datetime
from datetime import timedelta
import arrow
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    )
from arsenalweb.models.common import (
    DBSession,
    User,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='home', permission='view', renderer='arsenalweb:templates/home.pt')
def view_home(request):
    '''Handle requests for home UI route.'''

    page_title_type = '_'
    page_title_name = 'Home'
    auth_user = get_authenticated_user(request)

    # Used by the columns menu to determine what to show/hide.
    column_selectors = [
        {'name': 'created', 'pretty_name': 'Date Created'},
        {'name': 'description', 'pretty_name': 'Description'},
        {'name': 'status_id', 'pretty_name': 'Status ID'},
        {'name': 'status_name', 'pretty_name': 'Status Name'},
        {'name': 'updated', 'pretty_name': 'Date Update'},
        {'name': 'updated_by', 'pretty_name': 'Updated By'},
    ]

    return {
        'au': auth_user,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
    }
