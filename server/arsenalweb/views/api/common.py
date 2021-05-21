'''Arsenal API'''
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
import re
import logging
from datetime import datetime
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy.orm.dynamic import AppenderQuery
#import arsenalweb.models
from arsenalweb.models.common import (
    Group,
    User,
    get_name_id_list,
    localize_date,
    )
from arsenalweb.models.data_centers import (
    DataCenter,
    DataCenterAudit,
    )
from arsenalweb.models.ec2_instances import (
    Ec2Instance,
    Ec2InstanceAudit,
    )
from arsenalweb.models.hardware_profiles import (
    HardwareProfile,
    HardwareProfileAudit,
    )
from arsenalweb.models.ip_addresses import (
    IpAddress,
    IpAddressAudit,
    )
from arsenalweb.models.nodes import (
    Node,
    NodeAudit,
    )
from arsenalweb.models.node_groups import (
    NodeGroup,
    NodeGroupAudit,
    )
from arsenalweb.models.network_interfaces import (
    NetworkInterface,
    NetworkInterfaceAudit,
    )
from arsenalweb.models.operating_systems import (
    OperatingSystem,
    OperatingSystemAudit,
    )
from arsenalweb.models.physical_devices import (
    PhysicalDevice,
    PhysicalDeviceAudit,
    )
from arsenalweb.models.physical_elevations import (
    PhysicalElevation,
    PhysicalElevationAudit,
    )
from arsenalweb.models.physical_locations import (
    PhysicalLocation,
    PhysicalLocationAudit,
    )
from arsenalweb.models.physical_racks import (
    PhysicalRack,
    PhysicalRackAudit,
    )
from arsenalweb.models.statuses import (
    Status,
    StatusAudit,
    )
from arsenalweb.models.tags import (
    Tag,
    TagAudit,
    )
from arsenalweb.views import (
    get_authenticated_user,
    get_pag_params,
    )

LOG = logging.getLogger(__name__)
DATETIME_FIELDS = [
    'created',
    'updated',
    'last_registered',
]

# Common functions
def api_return_json(http_code, msg, total=0, result_count=0, results=None):
    '''Json format http responses with metadata added. If passed a tuple,
    list, dict or set, return a Response object. Otherwise return a
    dictionary that can be filtered through the model to render objects. Allows
    the use of the same function for both model-rendered types and json
    responses that are defined elsewhere.

    Args:

      http_code    : An integer representing the http response code.
      msg          : A string representing the message to return along with the code.
      results      : A list of results to include with the response.
      total        : An int that is the total number of results.
      result_count : An int that is the number of results returned by the
          current query. This is a subset of the total when pagination is used.
    '''

    if not results:
        res = []
    elif not isinstance(results, list):
        res = [results]
    else:
        res = results
    LOG.debug('RESULTS ARE: {0}'.format(results))

    resp = {
        'meta': {
            'total': total,
            'result_count': result_count,
        },
        'http_status': {
            'code': http_code,
            'message': msg,
        },
        'results': res
    }

    try:
        if not results or isinstance(res[0], (tuple, list, dict, set)):
            LOG.debug('Returning requests.Response...')
            return Response(json=resp,
                            content_type='application/json',
                            status_int=http_code)
        LOG.debug('Returning list of model rendered instance types: {0}'.format(type(results[0])))
        return resp
    except TypeError:
        LOG.debug('Returning single model rendered instance type: {0}'.format(type(results)))
        return resp

def api_200(msg='Command Successful', total=1, result_count=1, results=None):
    '''Return json formatted 200.'''

    return api_return_json(200, msg, total=total, result_count=result_count, results=results)

def api_400(msg='Bad Request'):
    '''Return json formatted 400.'''

    return api_return_json(400, msg)

def api_403(msg='Forbidden'):
    '''Return json formatted 403.'''

    return api_return_json(403, msg)

def api_404(msg='Not Found'):
    '''Return json formatted 404.'''

    return api_return_json(404, msg)

def api_409(msg='Conflict'):
    '''Return json formatted 409.'''

    return api_return_json(409, msg)

def api_500(msg='Internal server error'):
    '''Return json formatted 500.'''

    return api_return_json(500, msg)

def api_501(msg='Not Implemented'):
    '''Return json formatted 501.'''

    return api_return_json(501, msg)

def api_503(msg='Service Unavailable'):
    '''Return json formatted 503.'''

    return api_return_json(503, msg)

def collect_params(request, req_params, opt_params, auth_user_obj=False):
    '''Get values from the request, along with authenticated_user. Returns a
    dict of attributes if successful, raises an exception otherwise.

    request: pyramid request object.
    req_params: A list of all required params.
    opt_params: A list of all optional params. If not found, returns none.
    auth_user_obj: If set to true, will return the entire auth_user object
        instead of just the user_id.
    '''

    try:
        resp = {}
        auth_user = get_authenticated_user(request)
        resp['updated_by'] = auth_user['user_id']
        if auth_user_obj:
            resp['auth_user'] = auth_user
        payload = request.json_body

        for param in req_params:
            LOG.debug('Working on param: {0}'.format(param))
            try:
                resp[param] = payload[param].rstrip()
                LOG.debug('  is a string')
            # Handle integers
            except AttributeError:
                resp[param] = payload[param]
                LOG.debug('  is an int')
            except KeyError:
                msg = 'Required parameter: {0} missing from request!'.format(param)
                raise KeyError(msg)

        for param in opt_params:
            LOG.debug('Working on param: {0}'.format(param))
            try:
                resp[param] = payload[param].rstrip()
                LOG.debug('  is a string')
            # Handle integers
            except AttributeError:
                resp[param] = payload[param]
                LOG.debug('  is an int')
            except KeyError:
                resp[param] = None
                msg = 'Optional parameter: {0} missing from request. Setting ' \
                      'to None'.format(param)
                LOG.debug(msg)

        LOG.debug('Collected params: {0}'.format(resp))
        return resp

    except Exception:
        raise

def process_search(query, params, model_type, exact_get):
    '''Handle searches and delegate to exact or regex.'''

    # List of metaparams
    metaparams = [
        'exact_get',
        'fields',
        'perpage',
        'start',
    ]

    for key, val in params:

        if key in metaparams:
            continue

        # Force unique_id to lower since mac addrs can be represented both ways.
        if key == 'unique_id':
            val = val.lower()

        # Handy shortcuts - FIXME: this is specific to nodes and is going to need to
        # be addressd
        mutations = [
            'hardware_profile',
            'network_interface',
            'node_group',
            'operating_system',
            'status',
        ]

        muta = list(mutations)
        for mut in muta:
            mutations.append('ex_{0}'.format(mut))

        LOG.debug('MUTATIONS: {0}'.format(mutations))

        if key in mutations:
            key += '.name'

        if exact_get:
            query = process_exact_search(query, model_type, key, val)
        else:
            query = process_regex_search(query, model_type, key, val)

    return query

def process_regex_search(query, model_type, key, val):
    '''Handle searches with regex.'''

    LOG.debug('Regex search for model_type: {0} key: {1} '
              'value: {2}'.format(model_type, key, val))
    if '.' in key:
        query = filter_regex_subparam(query, model_type, key, val)
    else:
        if key in DATETIME_FIELDS:
            query = filter_datetime(query, model_type, key, val)
        elif ',' in val:
            query = filter_regex_multi_val(query, model_type, key, val)
        else:
            query = filter_regex(query, model_type, key, val)

    return query

def process_exact_search(query, model_type, key, val):
    '''Handle searches with exact_get.'''

    LOG.debug('Exact search for key: {0} value: {1}'.format(key, val))
    global_model = globals()[model_type]
    if ',' in val:
        query = query.filter(or_(getattr(global_model,
                                         key) == t for t in val.split(',')))
    else:
        query = query.filter(getattr(global_model, key) == val)

    return query

def filter_datetime(query, model_type, key, val):
    '''Deal with date searches. Return a sqlalchemy query object.

    Can be passed all or part of a date string, preceeded by a > (newer than)
    or < (older than), or two date strings comma separated for searching a
    range between the two dates (oldest date must be first).

    Examples:
        '>2020-08-06'
        '<2021-01-01'
        '2020-08-06 21:00:00,2020-08-07 16:00:00'
    '''

    LOG.debug('START: filter_datetime()')
    operator, key = check_regex_excludes(key)
    global_model = globals()[model_type]
    LOG.debug('Single value for model_type: %s key: %s value: %s '
              'operator: %s', model_type,
                              key,
                              val,
                              operator)
    my_val = val.split(',')
    if len(my_val) == 2:
        query = query.filter(getattr(global_model, key).between(my_val[0],
                                                                my_val[1]))
    else:
        oper = my_val[0][:1]
        sanitized_val = my_val[0][1:]
        LOG.debug('oper: %s sanitized_val: %s', oper, sanitized_val)
        if oper == '<':
            query = query.filter(getattr(global_model, key) <= sanitized_val)
        elif oper == '>':
            query = query.filter(getattr(global_model, key) >= sanitized_val)
        else:
            raise RuntimeError('Invalid operator for date search')

    LOG.debug('RETURN: filter_datetime()')
    return query

def filter_regex(query, model_type, key, val):
    '''Search for keys with a single value. Return a sqlalchemy query object.'''

    LOG.debug('START: filter_regex()')
    operator, key = check_regex_excludes(key)
    global_model = globals()[model_type]
    LOG.debug('Single value for model_type: {0} key: {1} value: {2} '
              'operator: {3}'.format(model_type,
                                     key,
                                     val,
                                     operator))
    query = query.filter(getattr(global_model,
                                 key).op(operator)(r'{0}'.format(val)))

    LOG.debug('RETURN: filter_regex()')
    return query

def filter_regex_multi_val(query, model_type, key, val):
    '''Search for keys with multiple values. Return a sqlalchemy query object.'''

    LOG.debug('START: filter_regex_multi_val()')
    operator, key = check_regex_excludes(key)
    LOG.debug('Multiple values for model_type: {0} key: {1} value: {2} '
              'operator: {3}'.format(model_type,
                                     key,
                                     val,
                                     operator))
    multi_val = val.replace(',', '|')
    global_model = globals()[model_type]
    query = query.filter(((getattr(global_model,
                                   key).op(operator)((r'{0}'.format(multi_val))))))

    LOG.debug('RETURN: filter_regex_multi_val()')
    return query

def filter_regex_subparam(query, model_type, key, val):
    '''Search for keys with sub parameters. Return a sqlalchemy query object.'''

    LOG.debug('START: filter_regex_subparam()')

    keysplit = key.split('.', 1)
    obj_type = keysplit[0]
    orig_obj_type = keysplit[0]
    operator, obj_type = check_regex_excludes(obj_type)
    obj_attrib = keysplit[1]
    obj_type_camel = underscore_to_camel(obj_type)

    LOG.debug('obj_type: {0} obj_type_camel: {1} obj_attrib: {2} '
              'val: {3} operator: {4}'.format(obj_type,
                                              obj_type_camel,
                                              obj_attrib,
                                              val,
                                              operator))

    list_types = [
        'guest_vm',
        'network_interface',
        'node_group',
        'tag',
    ]

    # Perform the join on non-list types, otherwise skip it.
    if obj_type not in list_types:
        LOG.debug('Searching for sub-param with join...')
        try:
            global_camel = globals()[obj_type_camel]
            global_model = globals()[model_type]
            name_id = '{0}_id'.format(obj_type)

            query = query.join(global_camel,
                               getattr(global_model, name_id)
                               ==
                               getattr(global_camel, 'id'))
        except Exception as ex:
            LOG.debug(ex)
            raise
    elif obj_type in list_types:
        LOG.debug('Searching for sub-param in association table...')
        obj_type_plural = plural_matcher(obj_type)

        LOG.debug('obj_type_plural is: {0}'.format(obj_type_plural))

        top_obj = getattr(globals()[model_type], obj_type_plural)
        if ',' in val:
            val = val.replace(',', '|')
        # joining lookup table with main object
        query = query.join(top_obj)
    else:
        LOG.debug('Searching for sub-param without join...')

    search_key = obj_attrib
    if orig_obj_type.startswith('ex_'):
        search_key = 'ex_{0}'.format(obj_attrib)
    LOG.debug('Mutated search key: {0}'.format(search_key))

    if ',' in val:
        query = filter_regex_multi_val(query, obj_type_camel, search_key, val)
    else:
        query = filter_regex(query, obj_type_camel, search_key, val)

    LOG.debug('RETURN: filter_regex_subparam()')
    return query

def check_regex_excludes(key):
    '''Checks a key to see if it's an exclude (starts with 'ex_'). Returns a
    not operator for regexp and a key.'''
    # Handle excludes
    operator = 'regexp'
    if key.startswith('ex_'):
        operator = 'not regexp'
        key = key[3:]

    return operator, key

def model_matcher(route_name):
    '''Matches routes to their model types.'''

    # FIXME: There has to be a better way than this.
    routes = {
        'api_data_center': 'DataCenter',
        'api_data_center_audit': 'DataCenterAudit',
        'api_data_center_audit_r': 'DataCenterAudit',
        'api_data_center_r': 'DataCenter',
        'api_data_centers': 'DataCenter',
        'api_data_centers_audit': 'DataCenterAudit',

        'api_ec2_instance': 'Ec2Instance',
        'api_ec2_instance_audit': 'Ec2InstanceAudit',
        'api_ec2_instance_audit_r': 'Ec2InstanceAudit',
        'api_ec2_instance_r': 'Ec2Instance',
        'api_ec2_instances': 'Ec2Instance',
        'api_ec2_instances_audit': 'Ec2InstanceAudit',

        'api_group': 'Group',
        'api_group_audit': 'GroupAudit',
        'api_group_audit_r': 'GroupAudit',
        'api_group_r': 'Group',
        'api_groups': 'Group',
        'api_groups_audit': 'GroupAudit',

        'api_hardware_profile': 'HardwareProfile',
        'api_hardware_profile_audit': 'HardwareProfileAudit',
        'api_hardware_profile_audit_r': 'HardwareProfileAudit',
        'api_hardware_profile_r': 'HardwareProfile',
        'api_hardware_profiles': 'HardwareProfile',
        'api_hardware_profiles_audit': 'HardwareProfileAudit',

        'api_hypervisor_vm_assignment': 'HypervisorVmAssignment',
        'api_hypervisor_vm_assignment_r': 'HypervisorVmAssignment',
        'api_hypervisor_vm_assignments': 'HypervisorVmAssignment',

        'api_ip_address': 'IpAddress',
        'api_ip_address_audit': 'IpAddressAudit',
        'api_ip_address_audit_r': 'IpAddressAudit',
        'api_ip_address_r': 'IpAddress',
        'api_ip_addresses': 'IpAddress',
        'api_ip_addresses_audit': 'IpAddressAudit',

        'api_network_interface': 'NetworkInterface',
        'api_network_interface_audit': 'NetworkInterfaceAudit',
        'api_network_interface_audit_r': 'NetworkInterfaceAudit',
        'api_network_interface_r': 'NetworkInterface',
        'api_network_interfaces': 'NetworkInterface',
        'api_network_interfaces_audit': 'NetworkInterfaceAudit',

        'api_node': 'Node',
        'api_node_audit': 'NodeAudit',
        'api_node_audit_r': 'NodeAudit',
        'api_node_r': 'Node',
        'api_nodes': 'Node',
        'api_nodes_audit': 'NodeAudit',

        'api_node_group': 'NodeGroup',
        'api_node_group_audit': 'NodeGroupAudit',
        'api_node_group_audit_r': 'NodeGroupAudit',
        'api_node_group_r': 'NodeGroup',
        'api_node_groups': 'NodeGroup',
        'api_node_groups_audit': 'NodeGroupAudit',

        'api_operating_system': 'OperatingSystem',
        'api_operating_system_audit': 'OperatingSystemAudit',
        'api_operating_system_audit_r': 'OperatingSystemAudit',
        'api_operating_system_r': 'OperatingSystem',
        'api_operating_systems': 'OperatingSystem',
        'api_operating_systems_audit': 'OperatingSystemAudit',

        'api_physical_device': 'PhysicalDevice',
        'api_physical_device_audit': 'PhysicalDeviceAudit',
        'api_physical_device_audit_r': 'PhysicalDeviceAudit',
        'api_physical_device_r': 'PhysicalDevice',
        'api_physical_devices': 'PhysicalDevice',
        'api_physical_devices_audit': 'PhysicalDeviceAudit',

        'api_physical_elevation': 'PhysicalElevation',
        'api_physical_elevation_audit': 'PhysicalElevationAudit',
        'api_physical_elevation_audit_r': 'PhysicalElevationAudit',
        'api_physical_elevation_r': 'PhysicalElevation',
        'api_physical_elevations': 'PhysicalElevation',
        'api_physical_elevations_audit': 'PhysicalElevationAudit',

        'api_physical_location': 'PhysicalLocation',
        'api_physical_location_audit': 'PhysicalLocationAudit',
        'api_physical_location_audit_r': 'PhysicalLocationAudit',
        'api_physical_location_r': 'PhysicalLocation',
        'api_physical_locations': 'PhysicalLocation',
        'api_physical_locations_audit': 'PhysicalLocationAudit',

        'api_physical_rack': 'PhysicalRack',
        'api_physical_rack_audit': 'PhysicalRackAudit',
        'api_physical_rack_audit_r': 'PhysicalRackAudit',
        'api_physical_rack_r': 'PhysicalRack',
        'api_physical_racks': 'PhysicalRack',
        'api_physical_racks_audit': 'PhysicalRackAudit',

        'api_status': 'Status',
        'api_status_audit': 'StatusAudit',
        'api_status_audit_r': 'StatusAudit',
        'api_status_r': 'Status',
        'api_statuses': 'Status',
        'api_statuses_audit': 'StatusAudit',

        'api_tag': 'Tag',
        'api_tag_audit': 'TagAudit',
        'api_tag_audit_r': 'TagAudit',
        'api_tag_r': 'Tag',
        'api_tags': 'Tag',
        'api_tags_audit': 'TagAudit',

        'api_user': 'User',
        'api_user_audit': 'UserAudit',
        'api_user_audit_r': 'UserAudit',
        'api_user_r': 'User',
        'api_users': 'User',
        'api_users_audit': 'UserAudit',
    }

    return routes[route_name]

def plural_matcher(object_type):
    '''Matches object types to their plurality.'''

    object_types = {
        'data_center': 'data_centers',
        'guest_vm': 'guest_vms',
        'ip_address': 'ip_addresses',
        'network_interface': 'network_interfaces',
        'node': 'nodes',
        'node_group': 'node_groups',
        'tag': 'tags',
    }

    return object_types[object_type]

def camel_to_underscore(model_type):
    '''Convert camel case to underscore for mapping.'''

    reg = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    camel = reg.sub(r' \1', model_type).lower().strip()
    camel = camel.replace(" ", "_")

    return camel

def underscore_to_camel(model_type):
    '''Convert underscore to camel case for mapping.'''

    underscore = model_type.split('_')
    return "".join(x.title() for x in underscore)

def validate_tag_perm(request, auth_user, tag_name):
    '''Validates that the authenticated user has permission to modify the tag.
    Returns True under the following conditions:

        - Tag does not match a regex in the protected list.
        - Tag matches a regex in the protected list and user is in an allowed group.
        - Secure tags is not configured in the main config file.

    Returns False otherwise.

    Params:

    request  : A pyramid.request object.
    auth_user: A dict returned from arsenalweb.views.get_authenticated_user()
    tag_name : The name of the tag to evaluate.
    '''

    LOG.debug('Validating tag name: {0}'.format(tag_name))

    settings = request.registry.settings
    try:
        # Since we are splitting on newline, use a list comp to eliminate the first
        # empty line.
        secure_tag_regexes = [s for s in settings['arsenal.secure_tags.list'].splitlines() if s]
        secure_groups = [s for s in settings['arsenal.secure_tags.groups'].splitlines() if s]
    except KeyError:
        LOG.warn('You must define arsenal.secure_tags.list and '
                 'arsenal.secure_tags.groups in the main settings file to '
                 'enable secure tags. Bypassing this feature.')
        return True

    LOG.debug('Secure tags regex list: {0}'.format(secure_tag_regexes))
    LOG.debug('Secure tags groups: {0}'.format(secure_groups))
    LOG.debug('Users is: {0}'.format(auth_user))

    try:
        for tag_regex in secure_tag_regexes:
            regex = re.compile(tag_regex)
            if re.match(regex, tag_name):
                LOG.debug('Secure tag detected: {0}'.format(tag_name))
                if not set(secure_groups) & set(auth_user['groups']):
                    LOG.error('User is not allowed to modify tag: {0}'.format(tag_name))
                    return False
                else:
                    LOG.debug('User is in an allowed group.')
                    return True
        LOG.debug('Tag is not secured: {0}'.format(tag_name))
        return True
    except:
        raise

@view_config(route_name='api_data_center_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_data_center_r', request_method='GET', renderer='json')
@view_config(route_name='api_ec2_instance_r', request_method='GET', renderer='json')
@view_config(route_name='api_ec2_instance_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_group_r', request_method='GET', renderer='json')
@view_config(route_name='api_group_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profile_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profile_r', request_method='GET', renderer='json')
@view_config(route_name='api_hypervisor_vm_assignment_r', request_method='GET', renderer='json')
@view_config(route_name='api_ip_address_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_ip_address_r', request_method='GET', renderer='json')
@view_config(route_name='api_network_interface_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_network_interface_r', request_method='GET', renderer='json')
@view_config(route_name='api_node_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_node_group_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_node_group_r', request_method='GET', renderer='json')
@view_config(route_name='api_node_r', request_method='GET', renderer='json')
@view_config(route_name='api_operating_system_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_operating_system_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_device_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_device_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevation_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevation_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_location_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_location_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_rack_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_physical_rack_r', request_method='GET', renderer='json')
@view_config(route_name='api_status_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_status_r', request_method='GET', renderer='json')
@view_config(route_name='api_tag_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_tag_r', request_method='GET', renderer='json')
@view_config(route_name='api_user_audit_r', request_method='GET', renderer='json')
@view_config(route_name='api_user_r', request_method='GET', renderer='json')
def get_api_attribute(request):
    '''Get single attribute request for /api/{object_type}/{id}/{resource}
       route match.'''

    LOG.debug('get_api_attribute()')
    try:
        model_type = model_matcher(request.matched_route.name)
        resource_id = request.matchdict['id']
        resource = request.matchdict['resource']
        LOG.debug('Querying for attribute={0},url={1}'.format(resource, request.url))

        query = request.dbsession.query(globals()[model_type])
        query = query.filter(getattr(globals()[model_type], 'id') == resource_id)
        query = query.one()
        LOG.debug('query is: {0}'.format(query))
        try:
            get_res = getattr(query, resource)
            LOG.debug(get_res)
        except Exception as ex:
            LOG.debug('exception: {0}'.format(repr(ex)))
            return api_500(msg=repr(ex))
        LOG.debug('resource: {0} get_res: {1}'.format(resource, get_res))

        if isinstance(get_res, AppenderQuery):
            if resource == 'tags':
                get_res = get_name_id_list(get_res, extra_keys=['value'])
            elif resource == 'network_interfaces':
                get_res = get_name_id_list(get_res, extra_keys=['unique_id'])
            else:
                get_res = get_name_id_list(get_res)

        # Handle datetime
        if isinstance(get_res, datetime):
            LOG.debug('Found datetime object.')
            get_res = localize_date(get_res)

        return {resource: get_res}

    except (NoResultFound, AttributeError) as ex:
        LOG.debug(ex)
        return api_404()
    except Exception as ex:
        msg = 'Error querying attribute: {0} exception: {1}'.format(request.url,
                                                                    repr(ex))
        LOG.error(msg)
        return api_500(msg=repr(ex))

@view_config(route_name='api_data_center', request_method='GET', renderer='json')
@view_config(route_name='api_ec2_instance', request_method='GET', renderer='json')
@view_config(route_name='api_group', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profile', request_method='GET', renderer='json')
@view_config(route_name='api_hypervisor_vm_assignment', request_method='GET', renderer='json')
@view_config(route_name='api_ip_address', request_method='GET', renderer='json')
@view_config(route_name='api_network_interface', request_method='GET', renderer='json')
@view_config(route_name='api_node', request_method='GET', renderer='json')
@view_config(route_name='api_node_group', request_method='GET', renderer='json')
@view_config(route_name='api_operating_system', request_method='GET', renderer='json')
@view_config(route_name='api_physical_device', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevation', request_method='GET', renderer='json')
@view_config(route_name='api_physical_location', request_method='GET', renderer='json')
@view_config(route_name='api_physical_rack', request_method='GET', renderer='json')
@view_config(route_name='api_status', request_method='GET', renderer='json')
@view_config(route_name='api_tag', request_method='GET', renderer='json')
@view_config(route_name='api_user', request_method='GET', renderer='json')
def api_read_by_id(request):
    '''Process get requests for /api/{object_type}/{id} route match.'''

    LOG.debug('START api_read_by_id()')
    try:
        model_type = model_matcher(request.matched_route.name)
        resource_id = request.matchdict['id']
        camel = camel_to_underscore(model_type)
        LOG.debug('Displaying single {0} id={1}'.format(camel, resource_id))

        query = request.dbsession.query(globals()[model_type])
        query = query.filter(getattr(globals()[model_type], 'id') == resource_id)
        query = query.one()

        LOG.debug('RETURN api_read_by_id()')

        return api_200(results=query)

    except NoResultFound:
        return api_404()

    except Exception as ex:
        msg = 'Error querying {0} url: {1} exception: {2}'.format(camel,
                                                                    request.url,
                                                                    repr(ex))
        LOG.error(msg)
        return api_500(msg=repr(ex))

@view_config(route_name='api_data_center_audit', request_method='GET', renderer='json')
@view_config(route_name='api_group_audit', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profile_audit', request_method='GET', renderer='json')
@view_config(route_name='api_ip_address_audit', request_method='GET', renderer='json')
@view_config(route_name='api_network_interface_audit', request_method='GET', renderer='json')
@view_config(route_name='api_node_audit', request_method='GET', renderer='json')
@view_config(route_name='api_node_group_audit', request_method='GET', renderer='json')
@view_config(route_name='api_operating_system_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_device_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevation_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_location_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_rack_audit', request_method='GET', renderer='json')
@view_config(route_name='api_status_audit', request_method='GET', renderer='json')
@view_config(route_name='api_tag_audit', request_method='GET', renderer='json')
@view_config(route_name='api_user_audit', request_method='GET', renderer='json')
def api_read_audit_by_id(request):
    '''Process get requests for /api/{object_type}_audit/{id} route match.
    Audit routes are different in that we use the matchdict id to look up the
    id of the resource in question instead of the primary key of the audit
    table.'''

    try:
        model_type = model_matcher(request.matched_route.name)
        resource_id = request.matchdict['id']
        camel = camel_to_underscore(model_type)
        LOG.debug('Displaying single {0} id={1}'.format(camel, resource_id))

        query = request.dbsession.query(globals()[model_type])
        query = query.filter(getattr(globals()[model_type],
                                     'object_id') == resource_id)
        query = query.all()
        total = len(query)

        return api_200(total=total, result_count=total, results=query)

    except NoResultFound:
        return api_404()

    except Exception as ex:
        msg = 'Error querying {0} url: {1} exception: {2}'.format(camel,
                                                                    request.url,
                                                                    repr(ex))
        LOG.error(msg)
        return api_500(msg=repr(ex))

@view_config(route_name='api_data_centers', request_method='GET', renderer='json')
@view_config(route_name='api_data_centers_audit', request_method='GET', renderer='json')
@view_config(route_name='api_ec2_instances', request_method='GET', renderer='json')
@view_config(route_name='api_ec2_instances_audit', request_method='GET', renderer='json')
@view_config(route_name='api_groups', request_method='GET', renderer='json')
@view_config(route_name='api_groups_audit', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profiles', request_method='GET', renderer='json')
@view_config(route_name='api_hardware_profiles_audit', request_method='GET', renderer='json')
@view_config(route_name='api_hypervisor_vm_assignments', request_method='GET', renderer='json')
@view_config(route_name='api_ip_addresses', request_method='GET', renderer='json')
@view_config(route_name='api_ip_addresses_audit', request_method='GET', renderer='json')
@view_config(route_name='api_network_interfaces', request_method='GET', renderer='json')
@view_config(route_name='api_network_interfaces_audit', request_method='GET', renderer='json')
@view_config(route_name='api_node_groups', request_method='GET', renderer='json')
@view_config(route_name='api_node_groups_audit', request_method='GET', renderer='json')
@view_config(route_name='api_nodes', request_method='GET', renderer='json')
@view_config(route_name='api_nodes_audit', request_method='GET', renderer='json')
@view_config(route_name='api_operating_systems', request_method='GET', renderer='json')
@view_config(route_name='api_operating_systems_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_devices', request_method='GET', renderer='json')
@view_config(route_name='api_physical_devices_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevations', request_method='GET', renderer='json')
@view_config(route_name='api_physical_elevations_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_locations', request_method='GET', renderer='json')
@view_config(route_name='api_physical_locations_audit', request_method='GET', renderer='json')
@view_config(route_name='api_physical_racks', request_method='GET', renderer='json')
@view_config(route_name='api_physical_racks_audit', request_method='GET', renderer='json')
@view_config(route_name='api_statuses', request_method='GET', renderer='json')
@view_config(route_name='api_statuses_audit', request_method='GET', renderer='json')
@view_config(route_name='api_tags', request_method='GET', renderer='json')
@view_config(route_name='api_tags_audit', request_method='GET', renderer='json')
@view_config(route_name='api_users', request_method='GET', renderer='json')
@view_config(route_name='api_users_audit', request_method='GET', renderer='json')
def api_read_by_params(request):
    '''Process get requests for /api/{object_type} route match.'''

    model_type = model_matcher(request.matched_route.name)
    camel = camel_to_underscore(model_type)
    (perpage, offset) = get_pag_params(request)

    try:
        exact_get = request.GET.get("exact_get", None)

        if request.params:

            query = request.dbsession.query(globals()[model_type])

            # This is a bit of a cheat. Filtering from most to least specific
            # speeds up the search dramatically. Alphabetical sort makes the
            # 'name' parameter (which usually is the most specific) come
            # before almost everything else by default.
            params = list(request.GET.items())

            exclude_params = sorted([x for x in params if x[0].startswith('ex_')])
            include_params = sorted([x for x in params if not x[0].startswith('ex_')])

            LOG.debug('include_params: %s exclude_params: %s', include_params, exclude_params)

            query = process_search(query, include_params, model_type, exact_get)
            # Process excludes at the end to ensure they're excluded.
            if exclude_params:
                query = process_search(query, exclude_params, model_type, exact_get)

            if perpage:
                LOG.debug('Query count START')
                total = query.count()
                LOG.debug('Query count END')
                LOG.debug('Query limit START')
                LOG.debug('Query limit: %s offset: %s', perpage, offset)
                myob = query.limit(perpage).offset(offset).all()
                LOG.debug('Query limit END')
            else:
                LOG.debug('Query all START')
                myob = query.all()
                total = len(myob)
                LOG.debug('Query all END')

            result_count = len(myob)

            LOG.debug('Returning Query results')
            return api_200(total=total, result_count=result_count, results=myob)

        LOG.debug('Displaying all %s', camel)
        query = request.dbsession.query(globals()[model_type])
        total = query.count()
        myob = query.all()

        return api_200(total=total, result_count=total, results=myob)

    # FIXME: Should AttributeError return something different?
    except (NoResultFound, AttributeError):
        return api_404()

    except Exception as ex:
        msg = 'Error querying {0} url: {1} exception: {2}'.format(camel,
                                                                    request.url,
                                                                    repr(ex))
        LOG.error(msg)
        return api_500(msg=repr(ex))

@view_config(route_name='api_data_center', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_ec2_instance', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_hardware_profile', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_hypervisor_vm_assignment', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_ip_address', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_network_interface', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_node', permission='node_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_node_group', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_operating_system', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_device', permission='physical_device_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_elevation', permission='physical_elevation_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_location', permission='physical_location_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_rack', permission='physical_rack_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_status', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_tag', permission='tag_delete', request_method='DELETE', renderer='json')
def api_delete_by_id(request):
    '''Process delete requests for /api/{object_type}/{id} route match.'''

    try:
        # FIXME: Will be used for auditing eventually. Would be nice to use
        # request.authenticated_userid, but I think this gets ugly when it's
        # an AD user. Need to test.
        auth_user = get_authenticated_user(request)
        model_type = model_matcher(request.matched_route.name)
        resource_id = request.matchdict['id']
        camel = camel_to_underscore(model_type)
        LOG.debug('Checking for id={0}'.format(resource_id))
        object_type = request.path_info.split('/')[2]

        query = request.dbsession.query(globals()[model_type])
        query = query.filter(getattr(globals()[model_type], 'id') == resource_id)
        query = query.one()

        try:
            unique_field = 'name'
            object_name = getattr(query, unique_field)
        except AttributeError:
            unique_field = 'serial_number'
            object_name = getattr(query, unique_field)

        if object_type == 'tags' and not validate_tag_perm(request, auth_user, object_name):
            return api_403()

        # Defines the key to log in the audit table for the given model type
        # why an object is deleted. If not in this list, will default to
        # 'name.'
        del_keys = {
            'Node': 'unique_id',
            'PhysicalDevice': 'serial_number',
        }

        utcnow = datetime.utcnow()

        try:
            deleted_key = del_keys[model_type]
        except KeyError:
            deleted_key = 'name'

        audit = globals()['{0}Audit'.format(model_type)]()
        setattr(audit, 'object_id', query.id)
        setattr(audit, 'field', deleted_key)
        setattr(audit, 'old_value', getattr(query, deleted_key))
        setattr(audit, 'new_value', 'deleted')
        setattr(audit, 'updated_by', auth_user['user_id'])
        setattr(audit, 'created', utcnow)

        request.dbsession.add(audit)

        LOG.info('Deleting {0}: {1} id: {2}'.format(unique_field, object_name, resource_id))
        request.dbsession.delete(query)
        request.dbsession.flush()

        return api_200()

    except NoResultFound:
        return api_404()

    except Exception as ex:
        msg = 'Error deleting id: {0} exception: {1}'.format(resource_id,
                                                             repr(ex))
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_data_centers', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_ec2_instances', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_hardware_profiles', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_hypervisor_vm_assignments', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_ip_addresses', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_network_interfaces', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_node_groups', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_nodes', permission='node_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_operating_systems', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_devices', permission='physical_device_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_elevations', permission='physical_elevation_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_locations', permission='physical_location_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_physical_racks', permission='physical_rack_delete', request_method='DELETE', renderer='json')
@view_config(route_name='api_statuses', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_tags', permission='tag_delete', request_method='DELETE', renderer='json')
def api_delete_by_params(request):
    '''Process delete requests for /api/{object_type} route match. Iterates
       over passed parameters.'''

    # FIXME: Is any of this used? If so it needs to be locked down.

    try:
        # FIXME: Should we enforce required parameters here?
        # Will be used for auditing
        auth_user = get_authenticated_user(request)
        # FIXME: Should we allow this to be set on the client, or hard code it to true,
        # requiring an # exact match? Might make sense since there is no confirmation,
        # it just deletes.
        exact_get = True
        model_type = model_matcher(request.matched_route.name)
        camel = camel_to_underscore(model_type)
        payload = request.json_body
        params = ''

        query = request.dbsession.query(globals()[model_type])

        for key, val in payload.items():
            # FIXME: This is sub-par. Need a better way to distinguish
            # meta params from search params without having to
            # pre-define everything.
            if key == 'exact_get':
                continue

            params += '{0}={1},'.format(key, val)
            if exact_get:
                LOG.debug('Exact filtering on {0}={1}'.format(key, val))
                query = query.filter(getattr(globals()[model_type], key) == val)
            else:
                LOG.debug('Loose filtering on {0}={1}'.format(key, val))
                query = query.filter(getattr(globals()[model_type], key).like('%{0}%'.format(val)))
        LOG.debug('Searching for {0} with params: {1}'.format(camel, params.rstrip(',')))

        query = query.one()

        # FIXME: Need auditing
        LOG.info('Deleting {0} with params: {1}'.format(camel, params.rstrip(',')))
        request.dbsession.delete(query)
        request.dbsession.flush()

        return api_200()

    except NoResultFound:
        return api_404()

    except Exception as ex:
        msg = 'Error deleting {0} with params: {1} exception: {2}'.format(camel,
                                                                          params.rstrip(','),
                                                                          repr(ex))
        LOG.error(msg)
        return api_500(msg=msg)
