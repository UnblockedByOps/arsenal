'''Arsenal UI'''
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
import grp
import pwd
import pam
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.session import signed_deserialize
from pyramid_ldap import groupfinder as ldap_groupfinder
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
import requests
from passlib.hash import sha512_crypt
from arsenalweb.models.common import (
    DBSession,
    Group,
    User,
    )

LOG = logging.getLogger(__name__)

def _api_get(request, uri, payload=None):
    '''GET request to the API.'''

    # Don't override fields if they are passed. Allows large objects to be
    # filtered down if need be without having to specify fields everywhere.
    if payload:
        if not 'fields' in payload:
            payload['fields'] = 'all'
    else:
        payload = {'fields': 'all'}

    verify_ssl = request.registry.settings['arsenal.verify_ssl']
    api_protocol = request.registry.settings['arsenal.api_protocol']
    api_host = request.host

    api_url = '{0}://{1}{2}'.format(api_protocol, api_host, uri)

    LOG.info('Requesting data from API: {0} params: {1}'.format(api_url, payload))
    resp = requests.get(api_url, verify=verify_ssl, params=payload)

    if resp.status_code == requests.codes.ok:
        LOG.debug('Response data: {0}'.format(resp.json()))
        return resp.json()
    elif resp.status_code == requests.codes.not_found:
        LOG.warn('404: Object not found.')
    else:
        msg = 'There was an error querying the API: ' \
              'http_status_code={0},reason={1},request={2}'.format(resp.status_code,
                                                                   resp.reason,
                                                                   api_url)
        LOG.error(msg)
        raise RuntimeError(msg)

    return None

def _api_put(request, uri, data=None):
    '''PUT request to the API.'''

    verify_ssl = request.registry.settings['arsenal.verify_ssl']
    api_protocol = request.registry.settings['arsenal.api_protocol']
    api_host = request.host
    headers = request.headers
    headers['content-type'] = 'application/json'

    api_url = '{0}://{1}{2}'.format(api_protocol, api_host, uri)

    LOG.info('Submitting data to API: {0} data: {1}'.format(api_url, data))
    resp = requests.put(api_url, verify=verify_ssl, headers=headers, data=data)

    if resp.status_code == requests.codes.ok:
        LOG.debug('Response data: {0}'.format(resp.json()))
        return resp.json()
    else:
        msg = 'There was an error querying the API: ' \
              'http_status_code={0},reason={1},request={2}'.format(resp.status_code,
                                                                   resp.reason,
                                                                   api_url)
        LOG.error(msg)
        raise RuntimeError(msg)

def contains(list, filter):
    for lst in list:
        if filter(lst):
            return True
    return False

def site_layout(level):
    '''Return the global layout.'''

    try:
        if level == 'min':
            renderer = get_renderer("arsenalweb:templates/min_layout.pt")
        elif level == 'audit':
            renderer = get_renderer("arsenalweb:templates/audit_layout.pt")
        else:
            renderer = get_renderer("arsenalweb:templates/global_layout.pt")
        layout = renderer.implementation().macros['layout']
    except:
        raise

    return layout

def global_groupfinder(userid, request):
    '''Wraps all groupfinders (ldap, pam and db) so we can use one callback in the auth policy.'''

    groups = None
    try:
        LOG.debug('Checking local groups for userid: {0}'.format(userid))
        # FIXME: Getting called twice
        groups = db_groupfinder(userid)
        if groups:
            LOG.debug('Found local groups for userid: {0} groups: {1}'.format(userid, groups))
    except Exception as ex:
        LOG.error('{0} ({1})'.format(Exception, ex))

    if request.registry.settings['arsenal.use_ldap'] and not groups:
        try:
            LOG.debug('Checking ldap groups for userid: {0}'.format(userid))
            groups = ldap_groupfinder(userid, request)
            if groups:
                LOG.debug('Found ldap groups for userid: {0} groups: {1}'.format(userid,
                                                                                 groups))
        except Exception as ex:
            LOG.error('{0} ({1})'.format(Exception, ex))

    if request.registry.settings['arsenal.use_pam'] and not groups:
        try:
            LOG.debug('Checking pam groups for userid: {0}'.format(userid))
            groups = pam_groupfinder(userid)
            if groups:
                LOG.debug('Found pam groups for userid: {0} groups: {1}'.format(userid,
                                                                                groups))
        except Exception as ex:
            LOG.error('{0} ({1})'.format(Exception, ex))

    return groups

def pam_groupfinder(userid):
    '''Queries pam for a list of groups the user belongs to. Returns either a list of
    groups (empty if no groups) or None if the user doesn't exist.'''

    groups = []
    try:
        groups = [g.gr_name for g in grp.getgrall() if userid in g.gr_mem]
        # Also add the user's default group
        gid = pwd.getpwnam(userid).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
    except Exception as ex:
        LOG.error('{0} ({1})'.format(Exception, ex))

    LOG.debug('User: {0} has the following groups: {1}'.format(userid, groups))
    return groups

def pam_authenticate(login, password):
    '''Checks the validity of a username/password against unix pam.'''

    try:
        pam_auth = pam.pam()
        if pam_auth.authenticate(login, password):
            return [login]
    except Exception as ex:
        LOG.error('{0} ({1})'.format(Exception, ex))

    return None

def db_groupfinder(userid):
    '''Queries the db for a list of groups the user belongs to. Returns either
       a list of groups (empty if no groups) or None if the user doesn't exist.'''

    groups = None
    try:
        user = DBSession.query(User).filter(User.name == userid).one()
        groups = [group.name for group in user.groups]
    except NoResultFound:
        LOG.debug('No DB groups for: %s', userid)
    except Exception as ex:
        LOG.error('{0} ({1})'.format(Exception, ex))

    LOG.debug('DB groups for user: %s are: %s', userid, groups)
    return groups

def db_authenticate(login, password):
    '''Checks the validity of a username/password against what is stored in the
    database.'''

    try:
        q = DBSession.query(User)
        q = q.filter(User.name == login)
        db_user = q.one()
    except Exception as e:
        LOG.debug("%s (%s)" % (Exception, e))
        # Should return invalid username here somehow
        return None

    try:
        if sha512_crypt.verify(password, db_user.password):
            LOG.debug('Successfully authenticated via local DB')
            return [login]
    except Exception as e:
        LOG.error('{0} ({1})'.format(Exception, e))

    return None

# FIXME: This whole thing sucks
def get_authenticated_user(request):
    '''Gets all the user information for an authenticated  user. Checks groups
    and permissions, and returns a dict of everything.'''

    authenticated_user = {
        'user_id': '',
        'login': '',
        'groups': '',
        'first': '',
        'last': '',
        'first_last': '',
        'auth': False,
        'prd_auth': False,
        'admin_auth': False,
        'cp_auth': False,
    }

    user_id = request.authenticated_userid
    first = ''
    last = ''
    groups = []

    try:
        user = DBSession.query(User).filter(User.name == user_id).one()
        first = user.first_name
        last = user.last_name
        # FIXME: Getting called twice
        groups = db_groupfinder(user_id)
        first_last = '{0} {1}'.format(first, last)
        auth = True
    except NoResultFound:
        LOG.debug('No db user for: {0}'.format(user_id))
    except Exception as ex:
        LOG.error('{0} ({1})'.format(Exception, ex))

    if request.registry.settings['arsenal.use_ldap'] and not groups:
        LOG.debug('Using LDAP...')
        try:
            (first, last) = format_user(user_id)
            groups = ldap_groupfinder(user_id, request)
            first_last = '{0} {1}'.format(first, last)
            auth = True
        except Exception as ex:
            LOG.error('{0} ({1})'.format(Exception, ex))

    if request.registry.settings['arsenal.use_pam'] and not groups:
        LOG.debug('Using PAM...')
        try:
            try:
                (first, last) = pwd.getpwnam(user_id).pw_gecos.split()
            except ValueError:
                first = user_id
            groups = pam_groupfinder(user_id)
            first_last = '{0} {1}'.format(first, last)
            auth = True
        except Exception as ex:
            LOG.error('{0} ({1})'.format(Exception, ex))

    try:
        login = validate_username_cookie(request.cookies['un'],
                                         request.registry.settings['arsenal.cookie_token'])
    except:
        return HTTPFound('/logout?message=Your cookie has been tampered with. You have been logged out')

    LOG.debug('first: {0} last: {1} first_last: {2} auth: {3} groups: {4}'.format(first,
                                                                                  last,
                                                                                  first_last,
                                                                                  auth,
                                                                                  groups))

    # authenticated user
    authenticated_user['user_id'] = user_id
    authenticated_user['login'] = login
    authenticated_user['groups'] = groups
    authenticated_user['first'] = first
    authenticated_user['last'] = last
    authenticated_user['first_last'] = first_last
    authenticated_user['loggedin'] = auth

    return authenticated_user

def format_user(user):
    '''Remove the extra stuff from ldap users for display purposes.'''

    (last_name, first_name, junk) = user.split(',', 2)
    last_name = last_name.rstrip('\\')
    last_name = last_name.strip('CN=')

    return(first_name, last_name)

def format_groups(groups):
    '''Remove the extra stuff from ldap group for display purposes.'''

    formatted = []
    for group in range(len(groups)):
        formatted.append(find_between(groups[group], 'CN=', ',OU='))
    return formatted

def find_between(srch, first, last):
    '''Find text in between two delimeters'''

    try:
        start = srch.index(first) + len(first)
        end = srch.index(last, start)
        return srch[start:end]
    except ValueError:
        return ""

def validate_username_cookie(cookieval, cookie_token):
    '''Returns the username if it validates. Otherwise throws
    an exception.'''

    return signed_deserialize(cookieval, cookie_token)

def get_pag_params(request):
    '''Parse and return page params.'''

    try:
        offset = int(request.GET.getone("start"))
    except KeyError:
        offset = 0

    try:
        perpage = int(request.GET.getone("perpage"))
    except KeyError:
        # Default limit the web UI to 50 results, no limit for the client.
        if request.path.startswith('/api/'):
            perpage = None
        else:
            perpage = 50

    return (perpage, offset)

def get_nav_urls(path, offset, perpage, total, payload=None):
    '''Format and return navigation urls.'''

    nav_urls = {}

    skip_keys = ['start', 'perpage', 'fields']
    for key in skip_keys:
        try:
            del payload[key]
        except KeyError:
            pass

    nav_start = '{0}?start={1}'.format(path, 0)
    nav_prev = '{0}?start={1}'.format(path, offset - perpage)
    nav_next = '{0}?start={1}'.format(path, offset + perpage)
    nav_end = '{0}?start={1}'.format(path, (total-1)/perpage*perpage)

    key_params = ''
    for key, val in payload.items():
        key_params += '&{0}={1}'.format(key, val)

    nav_urls['nav_start'] = '{0}{1}'.format(nav_start, key_params)
    nav_urls['nav_prev'] = '{0}{1}'.format(nav_prev, key_params)
    nav_urls['nav_next'] = '{0}{1}'.format(nav_next, key_params)
    nav_urls['nav_end'] = '{0}{1}'.format(nav_end, key_params)

    nav_urls['next_disable'] = False
    if (offset+perpage) >= total:
        nav_urls['next_disable'] = True

    return nav_urls
