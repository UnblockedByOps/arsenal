'''Arsenal login page.'''
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
from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPOk
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.session import signed_serialize
from pyramid_ldap import get_ldap_connector
from arsenalweb.views import (
    db_authenticate,
    get_authenticated_user,
    pam_authenticate,
    site_layout,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='login', renderer='arsenalweb:templates/login.pt')
@forbidden_view_config(renderer='arsenalweb:templates/login.pt')
def login(request):
    '''Process requests for the /login route.'''

    page_title = 'Login'

    LOG.debug('Processing login request...')

    auth_user = get_authenticated_user(request)

    if request.referer:
        referer_host = request.referer.split('/')[2]
    else:
        referer_host = None

    # Need to send the client a 401 so it can send a user/pass to auth.
    # Without this the client just gets the login page with a 200 and
    # thinks the command was successful.
    if request.path_info.split('/')[1][:3] == 'api' and not request.authenticated_userid:
        LOG.debug('request came from the api, sending request to re-auth')
        return HTTPUnauthorized()

    if request.referer and referer_host == request.host \
       and request.referer.split('/')[3][:6] != 'logout':
        return_url = request.referer
    elif request.path != '/login':
        return_url = request.url
    else:
        return_url = '/nodes'

    login_name = ''
    password = ''
    error = ''

    if 'form.submitted' in request.POST:
        login_name = request.POST['login']
        password = request.POST['password']

        LOG.debug('Attempting to authenticate login: {0}'.format(login_name))

        # Try local first, ldap/pam second (if configured)
        LOG.debug('Authenticating against local DB...')
        data = db_authenticate(login_name, password)

        if data is None and request.registry.settings['arsenal.use_ldap']:
            LOG.debug('Authenticating against LDAP...')
            connector = get_ldap_connector(request)
            data = connector.authenticate(login_name, password)

        if data is None and request.registry.settings['arsenal.use_pam']:
            LOG.debug('Authenticating against PAM...')
            data = pam_authenticate(login_name, password)

        if data is not None:
            user_name = data[0]
            encrypted = signed_serialize(login_name,
                                         request.registry.settings['arsenal.cookie_token'])
            headers = remember(request, user_name)
            headers.append(('Set-Cookie', 'un=' + str(encrypted) + '; Max-Age=604800; Path=/'))

            if 'api.client' in request.POST:
                return HTTPOk(headers=headers)
            else:
                return HTTPFound(request.POST['return_url'], headers=headers)
        else:
            error = 'Invalid credentials'
            request.response.status = 403

    if request.authenticated_userid:

        if request.path == '/login':
            error = 'You are already logged in'
            page_title = 'Already Logged In'
        else:
            error = 'You do not have permission to access this page'
            page_title = 'Access Denied'
            request.response.status = 403

    return {
        'au': auth_user,
        'error': error,
        'layout': site_layout('max'),
        'login': login_name,
        'page_title': page_title,
        'password': password,
        'return_url': return_url,
    }
