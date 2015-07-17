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
from pyramid.security import forget
import logging
from arsenalweb.views import (
    site_layout,
    )

@view_config(route_name='logout', renderer='arsenalweb:templates/logout.pt')
def logout(request):

    page_title = 'Login'
    message = None

    try:
        if request.params['message']:
            message = request.params['message']
    except:
        pass

    headers = forget(request)
    # Do I really need this?
    headers.append(('Set-Cookie', 'un=; Max-Age=0; Path=/'))
    request.response.headers = headers
    # No idea why I have to re-define these, but I do or it poops itself
    request.response.content_type = 'text/html'
    request.response.charset = 'UTF-8'
    request.response.status = '200 OK'
    
    return {'layout': site_layout('max'),
            'page_title': page_title,
            'message': message,
            }
