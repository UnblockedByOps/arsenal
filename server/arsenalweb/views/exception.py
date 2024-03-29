'''Arsenal exception view.'''
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

@view_config(context=Exception, renderer='arsenalweb:templates/exception.pt')
def error(exc, request):
    '''Serve up a custom exception page.'''

    request.response.status_int = 500
    page_title = 'Internal Server Error'

    return {
        'error': str(exc),
        'layout': site_layout('min'),
        'page_title_name': page_title,
    }
