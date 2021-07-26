'''Arsenal help UI.'''
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
    site_layout,
)

@view_config(route_name='help', renderer='arsenalweb:templates/help.pt')
def help_page(request):
    '''Handle requests for help UI route.'''

    page_title = 'Help'

    return {
        'layout': site_layout('max'),
        'page_title': page_title,
    }
