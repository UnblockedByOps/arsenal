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
from pyramid.config import Configurator
from .views import global_groupfinder
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.renderers import JSON
from pyramid_xml_renderer import XML
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy.exc import DisconnectionError
import ldap
import logging
import ConfigParser
import os
from .models import (
    DBSession,
    Base,
    Group,
    )


class RootFactory(object):

    # Additional ACLs loaded from the DB below
    __acl__ = [(Allow, Authenticated, 'view')]
    def __init__(self, request):
        pass


def getSettings(global_config, settings):
    # Secrets
    cp = ConfigParser.ConfigParser()
    cp.read(settings['arsenal.secrets_file'])
    for k,v in cp.items("app:main"):
        settings[k] = v

    scp = ConfigParser.SafeConfigParser()
    scp.read(global_config)
    for k,v in scp.items("app:safe"):
        settings[k] = v

    return settings


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except Exception, e:
        import sys
        print >> sys.stderr, "Error: %s (%s)" % (Exception, e)
        raise DisconnectionError()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings = getSettings(global_config['__file__'], settings)
    log = logging.getLogger(__name__)

    engine = engine_from_config(settings, 'sqlalchemy.')
    event.listen(engine, 'checkout', checkout_listener)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include('pyramid_chameleon')
    config.include('pyramid_ldap')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('user', '/user')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('help', '/help')
    config.add_route('search', '/search')
    config.add_route('nodes', '/nodes')
    config.add_route('node', '/nodes/{id}')
    config.add_route('node_groups', '/node_groups')
    config.add_route('node_group', '/node_groups/{id}')
    config.add_route('statuses', '/statuses')
    config.add_route('status', '/statuses/{id}')
    config.add_route('tags', '/tags')
    config.add_route('tag', '/tags/{id}')
    config.add_route('hardware_profiles', '/hardware_profiles')
    config.add_route('hardware_profile', '/hardware_profiles/{id}')
    config.add_route('operating_systems', '/operating_systems')
    config.add_route('operating_system', '/operating_systems/{id}')
    config.add_route('test', '/test')
    config.add_route('test2', '/test2')
    config.add_route('test3', '/test3')
    # API Endpoints. Order matters.
    # FIXME: api_register is a special endpoint in order to use pyramid 
    # secirty to control access to node registrations. Don't like it
    # but can't use request_param on a put request.
    config.add_route('api_register', '/api/register')
    config.add_route('api_nodes', '/api/nodes')
    config.add_route('api_node_r', '/api/nodes/{id}/{resource}')
    config.add_route('api_node', '/api/nodes/{id}')
    config.add_route('api_statuses', '/api/statuses')
    config.add_route('api_status_r', '/api/statuses/{id}/{resource}')
    config.add_route('api_status', '/api/statuses/{id}')
    config.add_route('api_tags', '/api/tags')
    config.add_route('api_tag_r', '/api/tags/{id}/{resource}')
    config.add_route('api_tag', '/api/tags/{id}')
    config.add_route('api_tag_node_assignments', '/api/tag_node_assignments')
    config.add_route('api_tag_node_assignment_r', '/api/tag_node_assignments/{id}/{resource}')
    config.add_route('api_tag_node_assignment', '/api/tag_node_assignments/{id}')
    config.add_route('api_tag_node_group_assignments', '/api/tag_node_group_assignments')
    config.add_route('api_tag_node_group_assignment_r', '/api/tag_node_group_assignments/{id}/{resource}')
    config.add_route('api_tag_node_group_assignment', '/api/tag_node_group_assignments/{id}')
    config.add_route('api_hardware_profiles', '/api/hardware_profiles')
    config.add_route('api_hardware_profile_r', '/api/hardware_profiles/{id}/{resource}')
    config.add_route('api_hardware_profile', '/api/hardware_profiles/{id}')
    config.add_route('api_operating_systems', '/api/operating_systems')
    config.add_route('api_operating_system_r', '/api/operating_systems/{id}/{resource}')
    config.add_route('api_operating_system', '/api/operating_systems/{id}')
    config.add_route('api_node_groups', '/api/node_groups')
    config.add_route('api_node_group_r', '/api/node_groups/{id}/{resource}')
    config.add_route('api_node_group', '/api/node_groups/{id}')
    config.add_route('api_node_group_assignments', '/api/node_group_assignments')
    config.add_route('api_node_group_assignment_r', '/api/node_group_assignments/{id}/{resource}')
    config.add_route('api_node_group_assignment', '/api/node_group_assignments/{id}')
    config.add_route('api_hypervisor_vm_assignments', '/api/hypervisor_vm_assignments')
    config.add_route('api_hypervisor_vm_assignment_r', '/api/hypervisor_vm_assignments/{id}/{resource}')
    config.add_route('api_hypervisor_vm_assignment', '/api/hypervisor_vm_assignments/{id}')

    config.add_renderer('json', JSON(indent=2))
    config.add_renderer('xml', XML())

    if settings['arsenal.use_ldap']:
        log.info('Configuring ldap users and groups')

        # Load the cert if it's defined and exists
        if os.path.isfile(settings['arsenal.ldap_cert']):
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings['arsenal.ldap_cert'])

        config.ldap_setup(
            settings['arsenal.ldap_server'] + ':' + settings['arsenal.ldap_port'],
            bind = settings['arsenal.ldap_bind'],
            passwd = settings['arsenal.ldap_password'],
            )

        config.ldap_set_login_query(
            base_dn = settings['arsenal.login_base_dn'],
            filter_tmpl = settings['arsenal.login_filter'],
            scope = ldap.SCOPE_SUBTREE,
            cache_period = 600,
            )

        config.ldap_set_groups_query(
            base_dn = settings['arsenal.group_base_dn'],
            filter_tmpl= settings['arsenal.group_filter'],
            scope = ldap.SCOPE_SUBTREE,
            cache_period = 600,
            )

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['arsenal.cookie_token'], callback=global_groupfinder, max_age=604800, hashalg='sha512')
        )

    config.set_authorization_policy(
        ACLAuthorizationPolicy()
        )

    # Load our groups and perms from the db and load them into the ACL
    try:
        r = DBSession.query(Group).all()
        for g in r:
            ga = g.get_all_assignments()
            if ga:
                ga = tuple(ga)
                log.info("Adding group: %s perm: %s" % (g.group_name, ga))
                RootFactory.__acl__.append([Allow, g.group_name, ga])
    except Exception, e:
        log.warn("%s (%s)" % (Exception, e))
                
    config.scan()
    return config.make_wsgi_app()
