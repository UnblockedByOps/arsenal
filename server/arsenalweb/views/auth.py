'''Arsenal Authentication'''
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
import re
from pwd import getpwnam
import pam
from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPOk
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import (
    remember,
    forget,
)
from pyramid.view import (
    forbidden_view_config,
    view_config,
)
from sqlalchemy.orm.exc import NoResultFound

from .. import models

LOG = logging.getLogger(__name__)


def authenticate_user(request):
    '''Authenticate a user. Check the DB first, then pam and ldap if enabled.
    Returns the user ID if successful, False otherwise.'''

    login_name = request.params['login']
    password = request.params['password']

    # Always try to find the user in the DB
    user_id =  db_authenticate(request, login_name, password)

    if request.registry.settings['arsenal.use_pam'] and not user_id:
        user_id =  pam_authenticate(login_name, password)

    if request.registry.settings['arsenal.use_ldap'] and not user_id:
        user_id = ldap_authenticate(login_name)

    return user_id

def db_authenticate(request, login_name, password):
    '''Checks the validity of a username/password against the Arsneal DB. Returns the
    user ID if successful, False otherwise.'''

    try:
        user = (
            request.dbsession.query(models.User)
            .filter_by(name=login_name)
            .one()
        )
        if user.check_password(password):
            LOG.debug('DB authentication successful for login: %s', login_name)
            return user.id
    except NoResultFound:
        LOG.debug('No db user for: %s', login_name)
    except Exception as ex:
        LOG.error('%s (%s)', Exception, ex)

    LOG.debug('DB authentication failed for login: %s', login_name)

    return False

def pam_authenticate(login_name, password):
    '''Checks the validity of a username/password against unix pam. Returns the
    user ID if successful, False otherwise.'''

    LOG.debug('Validating password for %s against PAM...', login_name)

    try:
        pam_auth = pam.pam()
        if pam_auth.authenticate(login_name, password):
            user_id = getpwnam(login_name)[2]
            LOG.debug('PAM authentication successful for login: %s', login_name)
            return user_id
    except Exception as ex:
        LOG.error('%s (%s)', Exception, ex)

    LOG.debug('PAM authentication failed for login: %s', login_name)

    return False

def ldap_authenticate(login_name):
    '''Checks the validity of a username/password against unix pam. Returns the
    user ID if successful, False otherwise.'''

    LOG.debug('Validating password for %s against LDAP not implemented...', login_name)
    return False

@view_config(route_name='login', renderer='arsenalweb:templates/login.pt')
def login(request):
    '''Handle user login requests.'''

    next_url = request.params.get('next', request.referrer)
    LOG.debug('REQUEST PARAMS: %s', request.params)
    error = ''

    if not next_url or re.match('.*\/login.*', next_url):
        try:
            next_url = request.params['next_url']
        except KeyError:
            LOG.debug('Redirecting from /login to /')
            next_url = request.route_url('home')

    LOG.debug('next_url is: %s', next_url)
    message = ''
    login_name = ''

    if request.method == 'POST':
        login_name = request.params['login']
        user_id = authenticate_user(request)
        LOG.debug('Authenticated user_id is: %s for user: %s', user_id, login_name)
        if user_id:
            new_csrf_token(request)
            headers = remember(request, user_id)
            LOG.debug('Returning redirect to next_url is: %s', next_url)
            return HTTPSeeOther(location=next_url, headers=headers)

        message = 'Failed login'
        request.response.status = 400

    return dict(
        message=message,
        url=request.route_url('login'),
        next_url=next_url,
        login=login_name,
        page_title='login',
        error = error,
    )

@view_config(route_name='api_login', request_method='POST')
def api_login(request):
    '''Handle API login requests.'''

    login_name = request.params['login']
    user_id = authenticate_user(request)
    LOG.debug('Authenticated user_id is: %s for user: %s', user_id, login_name)

    if user_id:
        new_csrf_token(request)
        headers = remember(request, user_id)
        return HTTPOk(headers=headers)

    return HTTPUnauthorized()

@view_config(route_name='logout')
def logout(request):
    '''Handle user logout requests.'''

    LOG.debug('Logging out user...')

    next_url = request.route_url('login')
    if request.method == 'GET':
        new_csrf_token(request)
        headers = forget(request)
        return HTTPSeeOther(location=next_url, headers=headers)

    return HTTPSeeOther(location=next_url)

@forbidden_view_config(renderer='arsenalweb:templates/403.pt')
def forbidden_view(exc, request):
    '''Handle forbidden requests.'''

    # Need to send the client a 401 so it can send a user/pass to auth.
    # Without this the client just gets the login page with a 200 and
    # thinks the command was successful.
    if request.path_info.split('/')[1][:3] == 'api' and not request.is_authenticated:
        LOG.debug('request came from the api, sending request to re-auth')
        return HTTPUnauthorized()

    if not request.is_authenticated:
        next_url = request.route_url('login', _query={'next': request.url})
        return HTTPSeeOther(location=next_url)

    request.response.status = 403
    return {
        'page_title_name': '403 Forbidden',
    }
