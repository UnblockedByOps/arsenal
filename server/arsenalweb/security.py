'Arsenal Security Policy.'
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
from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import (
    ACLHelper,
    Authenticated,
    Everyone,
)
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.request import RequestLocalCache
from sqlalchemy.orm.exc import NoResultFound

from . import models

LOG = logging.getLogger(__name__)


def global_groupfinder(request, userid):
    '''Wraps all groupfinders (ldap, pam and db) for the security policy.'''


    name, first_name, last_name, principals = db_groupfinder(request, userid)

    if not name and request.registry.settings['arsenal.use_pam']:
        name, first_name, last_name, principals = pam_groupfinder(request)

    if not name and request.registry.settings['arsenal.use_ldap']:
        name, first_name, last_name, principals = ldap_groupfinder()

    return name, first_name, last_name, principals

def db_groupfinder(request, userid):
    '''Queries the Arsenal DB for a list of groups the user belongs to. Returns basic user
       attributes and a list of group principals (empty if no groups) or None if the user
       doesn't exist.'''

    name = None
    first_name = None
    last_name = None
    principals = None

    try:
        user = request.dbsession.query(models.User).filter(models.User.id == userid).one()
        principals = ['group:' + group.name for group in user.groups]
        name = user.name
        first_name = user.first_name
        last_name = user.last_name
    except NoResultFound:
        LOG.debug('No DB principals for: %s', userid)
    except Exception as ex:
        LOG.error('%s (%s)', Exception, ex)

    if name:
        LOG.debug('DB principals for user: %s are: %s', userid, principals)
    return name, first_name, last_name, principals

def pam_groupfinder(request):
    '''Queries PAM for a list of groups the user belongs to. Returns basic user
       attributes and a list of group principals (empty if no groups) or None if the user
       doesn't exist.'''

    name = None
    first_name = None
    last_name = None
    principals = None

    try:
        name = pwd.getpwnam(request.identity['name'])[0]
        first_name = name
        groups = ['group:' + g.gr_name for g in grp.getgrall() if name in g.gr_mem]
        # Also add the user's default group
        gid = pwd.getpwnam(name).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
    except KeyError:
        LOG.debug('No DB principals for: %s', request.identity['name'])
    except Exception as ex:
        LOG.error('%s (%s)', Exception, ex)

    if name:
        LOG.debug('PAM principals for user: %s are: %s', name, principals)

    return name, first_name, last_name, principals

def ldap_groupfinder():
    '''Not yet implemented.'''
    return None, None, None, None


class ArsenalSecurityPolicy:
    '''Security policy for Arsenal.'''

    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret)

    def identity(self, request):
        '''define our simple identity as None or a dict with userid and
        principals keys.'''

        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity['userid']  # identical to the deprecated request.unauthenticated_userid

        # verify the userid, just like we did before with groupfinder
        name, first_name, last_name, principals = global_groupfinder(request, userid)
        groups = [gr.split(':')[1] for gr in principals if gr.startswith('group:')]

        # assuming the userid is valid, return a map with userid and principals
        if principals is not None:
            return {
                'userid': userid,
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'principals': principals,
                'groups': groups,
            }

    def authenticated_userid(self, request):
        '''Get authenticated user id. defer to the identity logic to determine if the user
        is logged in and return None if they are not.'''

        identity = request.identity
        if identity is not None:
            return identity['userid']

    def permits(self, request, context, permission):
        '''Use the identity to build a list of principals, and pass them
        to the ACLHelper to determine allowed/denied.'''

        identity = request.identity
        principals = set([Everyone])
        if identity is not None:
            principals.add(Authenticated)
            principals.add(identity['userid'])
            principals.update(identity['principals'])
        return ACLHelper().permits(context, principals, permission)

    def remember(self, request, userid, **kw):
        '''Remeber user.'''

        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        '''Forget user.'''

        return self.authtkt.forget(request, **kw)


def includeme(config):
    '''Add security policy to the pyramid config.'''

    LOG.debug('Loading security policy')

    settings = config.get_settings()

    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)

    config.set_security_policy(ArsenalSecurityPolicy(settings['arsenal.cookie_token']))
