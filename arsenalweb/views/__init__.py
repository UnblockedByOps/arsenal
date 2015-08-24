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
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.session import signed_deserialize
from pyramid_ldap import groupfinder as ldap_groupfinder
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
import logging
import requests
from passlib.hash import sha512_crypt
from arsenalweb.models import (
    DBSession,
    User,
    Group,
    )

log = logging.getLogger(__name__)


def _api_get(request, uri, payload=None):

    verify_ssl = request.registry.settings['arsenal.verify_ssl']
    api_protocol = request.registry.settings['arsenal.api_protocol']
    api_host = request.host

    api_url = '{0}://{1}{2}'.format(api_protocol, api_host, uri)

    log.info('Requesting data from API: {0} params: {1}'.format(api_url, payload))
    r = requests.get(api_url, verify=verify_ssl, params=payload)

    if r.status_code == requests.codes.ok:
        log.debug('Response data: %s' % r.json())
        return r.json()
    elif r.status_code == requests.codes.not_found:
        log.warn('404: Object not found.')
    else:
        log.error('There was an error querying the API: '
                  'http_status_code=%s,reason=%s,request=%s'
                  % (r.status_code, r.reason, api_url))

    return None


def _api_put(request, uri, data=None):

    verify_ssl = request.registry.settings['arsenal.verify_ssl']
    api_protocol = request.registry.settings['arsenal.api_protocol']
    api_host = request.host
    headers = request.headers
    headers['content-type'] = 'application/json'

    api_url = '{0}://{1}{2}'.format(api_protocol, api_host, uri)

    log.info('Submitting data to API: {0} data: {1}'.format(api_url, data))
    r = requests.put(api_url, verify=verify_ssl, headers=headers, data=data)

    if r.status_code == requests.codes.ok:
        log.debug('Response data: %s' % r.json())
        return r.json()
    else:
        log.error('There was an error querying the API: '
                      'http_status_code=%s,reason=%s,request=%s'
                      % (r.status_code, r.reason, api_url))
        return None


def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False


def site_layout(level):
    if level == 'min':
        renderer = get_renderer("arsenalweb:templates/min_layout.pt")
    else:
        renderer = get_renderer("arsenalweb:templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout


def global_groupfinder(userid, request):
    """ Wraps ldap and local groupfinders so we can use one callback
        in the auth policy """

    groups = None
    try:
        log.debug("Checking local groups for userid: %s" % (userid))
        # FIXME: Getting called twice
        groups = local_groupfinder(userid, request)
        if groups:
            log.debug("Found local groups for userid: %s groups: %s" % (userid, groups))
    except Exception as e:
        log.error("%s (%s)" % (Exception, e))
        pass

    if request.registry.settings['arsenal.use_ldap'] and not groups:
        try:
            log.debug("Checking ldap groups for userid: %s" % (userid))
            groups = ldap_groupfinder(userid, request)
            if groups:
                log.debug("Found ldap groups for userid: %s groups: %s" % (userid, groups))
        except Exception as e:
            log.error("%s (%s)" % (Exception, e))
            pass

    return groups


def local_groupfinder(userid, request):
    """ queries the db for a list of groups the user belongs to.
        Returns either a list of groups (empty if no groups) or None
        if the user doesn't exist. """

    groups = None
    try:
        user = DBSession.query(User).filter(User.user_name==userid).one()
        groups = user.get_all_assignments()
    except NoResultFound:
        log.debug('No local groups for: {0}'.format(userid))
    except Exception as e:
        log.error("%s (%s)" % (Exception, e))

    return groups


def local_authenticate(login, password):
    """ Checks the validity of a username/password against what
        is stored in the database. """

    try: 
        q = DBSession.query(User)
        q = q.filter(User.user_name == login)
        db_user = q.one()
    except Exception as e:
        log.debug("%s (%s)" % (Exception, e))
        # Should return invalid username here somehow
        return None

    try: 
        if sha512_crypt.verify(password, db_user.password):
            return [login]
    except Exception as e:
        log.error("%s (%s)" % (Exception, e))
        pass

    return None


def get_authenticated_user(request):
    """ Gets all the user information for an authenticated  user. Checks groups
        and permissions, and returns a dict of everything. """

    (first_last, user_id, login, groups, first, last, auth, prd_auth, admin_auth, cp_auth) = ('', '', '', '', '', '', False, False, False, False)

    user_id = request.authenticated_userid
    try:
        user = DBSession.query(User).filter(User.user_name==user_id).one()
        first = user.first_name
        last = user.last_name
        # FIXME: Getting called twice
        groups = local_groupfinder(user_id, request)
        first_last = "%s %s" % (first, last)
        auth = True
        log.debug("first: {0} last: {1} first_last: {2} auth: {3} groups: {4}".format(first, last, first_last, auth, groups))
    except NoResultFound:
        log.debug('No local user for: {0}'.format(user_id))
    except Exception as e:
        log.error("%s (%s)" % (Exception, e))

    if request.registry.settings['arsenal.use_ldap'] and not groups:
        try:
            (first,last) = format_user(user_id)
            groups = ldap_groupfinder(user_id, request)
            first_last = "%s %s" % (first, last)
            auth = True
        except Exception as e:
            log.error("%s (%s)" % (Exception, e))

    try:
        login = validate_username_cookie(request.cookies['un'], request.registry.settings['arsenal.cookie_token'])
    except:
        return HTTPFound('/logout?message=Your cookie has been tampered with. You have been logged out')

    # authenticated user
    au = {}
    au['user_id'] = user_id
    au['login'] = login
    au['groups'] = groups
    au['first'] = first
    au['last'] = last
    au['loggedin'] = auth
    au['first_last'] = first_last

    return (au)


def get_all_groups():
    """ Gets all the groups that are configured in
        the db and returns a dict of everything. """

    # Get the groups from the db
    group_perms = []
    r = DBSession.query(Group).all()
    for g in range(len(r)):
        ga = r[g].get_all_assignments()
        if ga:
            ga = tuple(ga)
            group_perms.append([r[g].group_name, ga])

    return(group_perms)


def format_user(user):
    # Make the name readable
    (last,first,junk) = user.split(',',2)
    last = last.rstrip('\\')
    last = last.strip('CN=')
    return(first,last)


def format_groups(groups):

    formatted = []
    for g in range(len(groups)):
        formatted.append(find_between(groups[g], 'CN=', ',OU='))
    return formatted

 
def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def validate_username_cookie(cookieval, cookie_token):
    """ Returns the username if it validates. Otherwise throws
    an exception"""

    return signed_deserialize(cookieval, cookie_token)


def get_pag_params(request):
    """Parse and return page params"""

    perpage = 40

    try:
        offset = int(request.GET.getone("start"))
    except KeyError:
        offset = 0

    return (perpage, offset)

