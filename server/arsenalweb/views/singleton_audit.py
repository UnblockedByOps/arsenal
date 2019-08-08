'''Arsenal audit routes singleton object types.'''
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
from pyramid.view import view_config
from arsenalweb.views import (
    _api_get,
    get_authenticated_user,
    site_layout,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='data_center_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='hardware_profile_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='ip_address_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='network_interface_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='node_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='node_group_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='operating_system_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='physical_device_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='physical_location_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='physical_rack_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='status_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
@view_config(route_name='tag_audit', permission='view', renderer='arsenalweb:templates/singleton_audit.pt')
def view_singleton_audit(request):
    '''Handle all audit routes for object types that are
    singletons (non-list, non-dict).'''

    meta = {
        'data_center_audit': {
            'page_type': 'Data Center',
            'object_type': 'data_centers',
        },
        'hardware_profile_audit': {
            'page_type': 'Hardware Profile',
            'object_type': 'hardware_profiles',
        },
        'ip_address_audit': {
            'page_type': 'IpAddress',
            'object_type': 'ip_addresses',
        },
        'network_interface_audit': {
            'page_type': 'NetworkInterface',
            'object_type': 'network_interfaces',
        },
        'node_audit': {
            'page_type': 'Node',
            'object_type': 'nodes',
        },
        'node_group_audit': {
            'page_type': 'Node Group',
            'object_type': 'node_groups',
        },
        'operating_system_audit': {
            'page_type': 'Operating System',
            'object_type': 'operating_systems',
        },
        'physical_device_audit': {
            'page_type': 'Physical Devices',
            'object_type': 'physical_devices',
        },
        'physical_location_audit': {
            'page_type': 'Physical Locations',
            'object_type': 'physical_locations',
        },
        'physical_rack_audit': {
            'page_type': 'Physical Racks',
            'object_type': 'physical_racks',
        },
        'status_audit': {
            'page_type': 'Status',
            'object_type': 'statuses',
        },
        'tag_audit': {
            'page_type': 'Tag',
            'object_type': 'tags',
        },
    }

    params = meta[request.matched_route.name]

    auth_user = get_authenticated_user(request)
    page_title = '{0}_audit'.format(params['object_type'])

    uri = '/api/{0}_audit/{1}'.format(params['object_type'], request.matchdict['id'])
    object_audit = _api_get(request, uri)

    return {
        'au': auth_user,
        'layout': site_layout('audit'),
        'object_audit': object_audit['results'],
        'page_title_name': page_title,
        'params': params,
    }
