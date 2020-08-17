'''Arsenal Pyramid WSGI application.'''
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
import ConfigParser
import os
import time
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.renderers import JSON
from pyramid_xml_renderer import XML
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy.exc import DisconnectionError
import ldap
from .views import global_groupfinder
from .models.common import (
    DBSession,
    Base,
    Group,
)


class RootFactory(object):
    '''Top level ACL class.'''

    # Additional ACLs loaded from the DB below
    __acl__ = [
        (Allow, Authenticated, ('view', 'tag_write', 'tag_delete'))
    ]
    def __init__(self, request):
        pass

def get_settings(global_config, settings):
    '''Read in settings from config files.'''

    # Secrets
    mcp = ConfigParser.ConfigParser()
    mcp.read(settings['arsenal.secrets_file'])
    for key, val in mcp.items("app:main"):
        settings[key] = val

    scp = ConfigParser.SafeConfigParser()
    scp.read(global_config)
    for key, val in scp.items("app:safe"):
        settings[key] = val

    return settings

def checkout_listener(dbapi_con, con_record, con_proxy):
    '''Test the listener.'''

    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except Exception, ex:
        import sys
        print >> sys.stderr, "Error: %s (%s)" % (Exception, ex)
        raise DisconnectionError()

def main(global_config, **settings):
    '''This function returns a Pyramid WSGI application.'''

    settings = get_settings(global_config['__file__'], settings)

    # Have to do this becasue it can be a boolean or a string.
    if settings['arsenal.verify_ssl'] == 'True':
        settings['arsenal.verify_ssl'] = bool(settings['arsenal.verify_ssl'])

    if settings['arsenal.verify_ssl'] == 'False':
        settings['arsenal.verify_ssl'] = bool('')

    log = logging.getLogger(__name__)

    engine = engine_from_config(settings, 'sqlalchemy.')
    event.listen(engine, 'checkout', checkout_listener)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    #
    # Routes
    #
    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include('pyramid_chameleon')
    config.include('pyramid_ldap')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('user', '/user')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('healthcheck', '/healthcheck')
    config.add_route('help', '/help')
    config.add_route('search', '/search')
    config.add_route('data_centers', '/data_centers')
    config.add_route('data_center', '/data_centers/{id}')
    config.add_route('data_centers_audit', '/data_centers_audit')
    config.add_route('data_center_audit', '/data_centers_audit/{id}')
    config.add_route('ip_addresses', '/ip_addresses')
    config.add_route('ip_address', '/ip_addresses/{id}')
    config.add_route('ip_addresses_audit', '/ip_addresses_audit')
    config.add_route('ip_address_audit', '/ip_addresses_audit/{id}')
    config.add_route('network_interfaces', '/network_interfaces')
    config.add_route('network_interface', '/network_interfaces/{id}')
    config.add_route('network_interfaces_audit', '/network_interfaces_audit')
    config.add_route('network_interface_audit', '/network_interfaces_audit/{id}')
    config.add_route('nodes', '/nodes')
    config.add_route('node', '/nodes/{id}')
    config.add_route('nodes_audit', '/nodes_audit')
    config.add_route('node_audit', '/nodes_audit/{id}')
    config.add_route('node_groups', '/node_groups')
    config.add_route('node_group', '/node_groups/{id}')
    config.add_route('node_groups_audit', '/node_groups_audit')
    config.add_route('node_group_audit', '/node_groups_audit/{id}')
    config.add_route('physical_locations', '/physical_locations')
    config.add_route('physical_location', '/physical_locations/{id}')
    config.add_route('physical_locations_audit', '/physical_locations_audit')
    config.add_route('physical_location_audit', '/physical_locations_audit/{id}')
    config.add_route('physical_devices', '/physical_devices')
    config.add_route('physical_device', '/physical_devices/{id}')
    config.add_route('physical_devices_audit', '/physical_devices_audit')
    config.add_route('physical_device_audit', '/physical_devices_audit/{id}')
    config.add_route('physical_elevations', '/physical_elevations')
    config.add_route('physical_elevation', '/physical_elevations/{id}')
    config.add_route('physical_elevations_audit', '/physical_elevations_audit')
    config.add_route('physical_elevation_audit', '/physical_elevations_audit/{id}')
    config.add_route('physical_racks', '/physical_racks')
    config.add_route('physical_rack', '/physical_racks/{id}')
    config.add_route('physical_racks_audit', '/physical_racks_audit')
    config.add_route('physical_rack_audit', '/physical_racks_audit/{id}')
    config.add_route('render_rack', '/render_rack')
    config.add_route('statuses', '/statuses')
    config.add_route('status', '/statuses/{id}')
    config.add_route('statuses_audit', '/statuses_audit')
    config.add_route('status_audit', '/statuses_audit/{id}')
    config.add_route('tags', '/tags')
    config.add_route('tag', '/tags/{id}')
    config.add_route('tags_audit', '/tags_audit')
    config.add_route('tag_audit', '/tags_audit/{id}')
    config.add_route('hardware_profiles', '/hardware_profiles')
    config.add_route('hardware_profile', '/hardware_profiles/{id}')
    config.add_route('hardware_profiles_audit', '/hardware_profiles_audit')
    config.add_route('hardware_profile_audit', '/hardware_profiles_audit/{id}')
    config.add_route('operating_systems', '/operating_systems')
    config.add_route('operating_system', '/operating_systems/{id}')
    config.add_route('operating_systems_audit', '/operating_systems_audit')
    config.add_route('operating_system_audit', '/operating_systems_audit/{id}')
    #
    # API Endpoints. Order matters.
    #
    # api_register is a special endpoint in order to use pyramid
    # secirty to control access to node registrations. Don't love it
    # but can't use request_param on a put request.
    config.add_route('api_register', '/api/register')
    config.add_route('api_enc', '/api/enc')

    config.add_route('api_data_centers', '/api/data_centers')
    config.add_route('api_data_center_r', '/api/data_centers/{id}/{resource}')
    config.add_route('api_data_center', '/api/data_centers/{id}')
    config.add_route('api_data_centers_audit', '/api/data_centers_audit')
    config.add_route('api_data_center_audit_r', '/api/data_centers_audit/{id}/{resource}')
    config.add_route('api_data_center_audit', '/api/data_centers_audit/{id}')

    config.add_route('api_nodes', '/api/nodes')
    config.add_route('api_node_r', '/api/nodes/{id}/{resource}')
    config.add_route('api_node', '/api/nodes/{id}')
    config.add_route('api_nodes_audit', '/api/nodes_audit')
    config.add_route('api_node_audit_r', '/api/nodes_audit/{id}/{resource}')
    config.add_route('api_node_audit', '/api/nodes_audit/{id}')

    config.add_route('api_statuses', '/api/statuses')
    config.add_route('api_status_r', '/api/statuses/{id}/{resource}')
    config.add_route('api_status', '/api/statuses/{id}')
    config.add_route('api_statuses_audit', '/api/statuses_audit')
    config.add_route('api_status_audit_r', '/api/statuses_audit/{id}/{resource}')
    config.add_route('api_status_audit', '/api/statuses_audit/{id}')

    config.add_route('api_tags', '/api/tags')
    config.add_route('api_tag_r', '/api/tags/{id}/{resource}')
    config.add_route('api_tag', '/api/tags/{id}')
    config.add_route('api_tags_audit', '/api/tags_audit')
    config.add_route('api_tag_audit_r', '/api/tags_audit/{id}/{resource}')
    config.add_route('api_tag_audit', '/api/tags_audit/{id}')

    config.add_route('api_hardware_profiles', '/api/hardware_profiles')
    config.add_route('api_hardware_profile_r', '/api/hardware_profiles/{id}/{resource}')
    config.add_route('api_hardware_profile', '/api/hardware_profiles/{id}')
    config.add_route('api_hardware_profiles_audit', '/api/hardware_profiles_audit')
    config.add_route('api_hardware_profile_audit_r', '/api/hardware_profiles_audit/{id}/{resource}')
    config.add_route('api_hardware_profile_audit', '/api/hardware_profiles_audit/{id}')

    config.add_route('api_ip_addresses', '/api/ip_addresses')
    config.add_route('api_ip_address_r', '/api/ip_addresses/{id}/{resource}')
    config.add_route('api_ip_address', '/api/ip_addresses/{id}')
    config.add_route('api_ip_addresses_audit', '/api/ip_addresses_audit')
    config.add_route('api_ip_address_audit_r', '/api/ip_addresses_audit/{id}/{resource}')
    config.add_route('api_ip_address_audit', '/api/ip_addresses_audit/{id}')

    config.add_route('api_operating_systems', '/api/operating_systems')
    config.add_route('api_operating_system_r', '/api/operating_systems/{id}/{resource}')
    config.add_route('api_operating_system', '/api/operating_systems/{id}')
    config.add_route('api_operating_systems_audit', '/api/operating_systems_audit')
    config.add_route('api_operating_system_audit_r', '/api/operating_systems_audit/{id}/{resource}')
    config.add_route('api_operating_system_audit', '/api/operating_systems_audit/{id}')

    config.add_route('api_physical_devices', '/api/physical_devices')
    config.add_route('api_physical_device_r', '/api/physical_devices/{id}/{resource}')
    config.add_route('api_physical_device', '/api/physical_devices/{id}')
    config.add_route('api_physical_devices_audit', '/api/physical_devices_audit')
    config.add_route('api_physical_device_audit_r', '/api/physical_devices_audit/{id}/{resource}')
    config.add_route('api_physical_device_audit', '/api/physical_devices_audit/{id}')

    config.add_route('api_physical_elevations', '/api/physical_elevations')
    config.add_route('api_physical_elevation_r', '/api/physical_elevations/{id}/{resource}')
    config.add_route('api_physical_elevation', '/api/physical_elevations/{id}')
    config.add_route('api_physical_elevations_audit', '/api/physical_elevations_audit')
    config.add_route('api_physical_elevation_audit_r', '/api/physical_elevations_audit/{id}/{resource}')
    config.add_route('api_physical_elevation_audit', '/api/physical_elevations_audit/{id}')

    config.add_route('api_physical_locations', '/api/physical_locations')
    config.add_route('api_physical_location_r', '/api/physical_locations/{id}/{resource}')
    config.add_route('api_physical_location', '/api/physical_locations/{id}')
    config.add_route('api_physical_locations_audit', '/api/physical_locations_audit')
    config.add_route('api_physical_location_audit_r', '/api/physical_locations_audit/{id}/{resource}')
    config.add_route('api_physical_location_audit', '/api/physical_locations_audit/{id}')

    config.add_route('api_physical_racks', '/api/physical_racks')
    config.add_route('api_physical_rack_r', '/api/physical_racks/{id}/{resource}')
    config.add_route('api_physical_rack', '/api/physical_racks/{id}')
    config.add_route('api_physical_racks_audit', '/api/physical_racks_audit')
    config.add_route('api_physical_rack_audit_r', '/api/physical_racks_audit/{id}/{resource}')
    config.add_route('api_physical_rack_audit', '/api/physical_racks_audit/{id}')

    config.add_route('api_node_groups', '/api/node_groups')
    config.add_route('api_node_group_r', '/api/node_groups/{id}/{resource}')
    config.add_route('api_node_group', '/api/node_groups/{id}')
    config.add_route('api_b_node_groups_deassign', '/api/bulk/node_groups/deassign')
    config.add_route('api_node_groups_audit', '/api/node_groups_audit')
    config.add_route('api_node_group_audit_r', '/api/node_groups_audit/{id}/{resource}')
    config.add_route('api_node_group_audit', '/api/node_groups_audit/{id}')

    config.add_route('api_hypervisor_vm_assignments', '/api/hypervisor_vm_assignments')
    config.add_route('api_hypervisor_vm_assignment_r', '/api/hypervisor_vm_assignments/{id}/{resource}')
    config.add_route('api_hypervisor_vm_assignment', '/api/hypervisor_vm_assignments/{id}')

    config.add_route('api_ec2_instances', '/api/ec2_instances')
    config.add_route('api_ec2_instance_r', '/api/ec2_instances/{id}/{resource}')
    config.add_route('api_ec2_instance', '/api/ec2_instances/{id}')
    config.add_route('api_ec2_instances_audit', '/api/ec2_instances_audit')
    config.add_route('api_ec2_instance_audit_r', '/api/ec2_instances_audit/{id}/{resource}')
    config.add_route('api_ec2_instance_audit', '/api/ec2_instances_audit/{id}')

    config.add_route('api_network_interfaces', '/api/network_interfaces')
    config.add_route('api_network_interface_r', '/api/network_interfaces/{id}/{resource}')
    config.add_route('api_network_interface', '/api/network_interfaces/{id}')
    config.add_route('api_network_interfaces_audit', '/api/network_interfaces_audit')
    config.add_route('api_network_interface_audit_r', '/api/network_interfaces_audit/{id}/{resource}')
    config.add_route('api_network_interface_audit', '/api/network_interfaces_audit/{id}')

    config.add_route('api_reports_db', '/api/reports/db')
    config.add_route('api_reports_nodes', '/api/reports/nodes')
    config.add_route('api_reports_stale_nodes', '/api/reports/stale_nodes')

    config.add_route('api_testing', '/api/testing')

    config.add_renderer('json', JSON(indent=2, sort_keys=True))
    config.add_renderer('xml', XML())

    if settings['arsenal.use_ldap']:
        log.info('Configuring ldap users and groups')

        # Load the cert if it's defined and exists
        if os.path.isfile(settings['arsenal.ldap_cert']):
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings['arsenal.ldap_cert'])

        config.ldap_setup(
            settings['arsenal.ldap_server'] + ':' + settings['arsenal.ldap_port'],
            bind=settings['arsenal.ldap_bind'],
            passwd=settings['arsenal.ldap_password'],
            )

        config.ldap_set_login_query(
            base_dn=settings['arsenal.login_base_dn'],
            filter_tmpl=settings['arsenal.login_filter'],
            scope=ldap.SCOPE_SUBTREE,
            cache_period=600,
            )

        config.ldap_set_groups_query(
            base_dn=settings['arsenal.group_base_dn'],
            filter_tmpl=settings['arsenal.group_filter'],
            scope=ldap.SCOPE_SUBTREE,
            cache_period=600,
            )

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['arsenal.cookie_token'],
                                    callback=global_groupfinder,
                                    max_age=604800,
                                    hashalg='sha512')
        )

    config.set_authorization_policy(
        ACLAuthorizationPolicy()
        )

    # Load our groups and perms from the db and load them into the ACL
    max_retries = 10
    for retry in range(1, max_retries):
        try:
            resp = DBSession.query(Group).all()
            for group in resp:
                gr_ass = group.get_all_assignments()
                if gr_ass:
                    gr_ass = tuple(gr_ass)
                    log.info('Adding group: {0} perm: {1}'.format(group.group_name,
                                                                  gr_ass))
                    RootFactory.__acl__.append([Allow, group.group_name, gr_ass])
        except Exception as ex:
            log.warn('Unable to load ACLs from database({0} of {1})! Exception: '
                     '{2}'.format(retry,
                                  max_retries,
                                  repr(ex)))
            sleep_secs = 5
            log.warn('Sleeping {0} seconds before retrying'.format(sleep_secs))
            time.sleep(sleep_secs)
        else:
            break
    else:
        log.warn('Unable to load ACLs from database after {0} retries! '
                 'Continuing in an ACL-less universe.'.format(max_retries))

    config.scan()
    return config.make_wsgi_app()
