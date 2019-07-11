'''Arsenal client common command line helper functions.

These functions support the functions that are called directly by
args.func() to invoke the appropriate action.

'''
#
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
from __future__ import print_function
import sys
import logging
import json
import re
import yaml

LOG = logging.getLogger(__name__)

def _check_tags(obj, set_tags):
    '''Check for tags that will be changed or removed.'''

    resp = ''
    try:
        tags = [tag for tag in set_tags.split(',')]
    # No tags
    except AttributeError:
        return resp

    for tag in tags:
        LOG.debug('Working on tag: {0}'.format(tag))
        key, val = tag.split('=')
        LOG.debug('name is: {0}'.format(obj['name']))
        LOG.debug('tags are: {0}'.format(obj['tags']))
        for obj_tag in obj['tags']:
            if key == obj_tag['name']:
                resp += '     Existing tag found: {0}={1} value will be updated ' \
                        'to: {2}\n'.format(obj_tag['name'], obj_tag['value'], val)

    return resp.rstrip()

def check_resp(resp):
    '''Check the http response code and exit non-zero if it's not a 200.'''

    LOG.debug('Checking status of http response: {0}'.format(json.dumps(resp,
                                                                        sort_keys=True,
                                                                        indent=2)))
    if resp['http_status']['code'] != 200:
        sys.exit(1)

def gen_help(help_type):
    '''Generate the list of searchable terms for help'''

    terms = {
        'data_centers_search': [
            'id',
            'name',
            'status',
        ],
        'ip_addresses_search': [
            'id',
            'ip_address',
        ],
        'network_interfaces_search': [
            'id',
            'name',
            'unique_id',
            'bond_master',
            'ip_address_id',
            'port_description',
            'port_number',
            'port_switch',
            'port_vlan',
        ],
        'nodes_search': [
            'id',
            'name',
            'unique_id',
            'status_id',
            'status',
            'hardware_profile_id',
            'hardware_profile',
            'operating_system_id',
            'operating_system',
            'uptime',
            'node_groups',
            'created',
            'updated',
            'updated_by',
        ],
        'node_groups_search': [
            'id',
            'name',
            'node_group_owner',
            'description',
            'notes_url',
        ],
        'physical_devices_search': [
            'id',
            'serial_number',
            'physical_elevation',
            'physical_location',
            'physical_rack',
            'hardware_profile',
            'oob_ip_address',
            'oob_mac_address',
        ],
        'physical_locations_search': [
            'id',
            'name',
            'provider',
            'address_1',
            'address_2',
            'city',
            'admin_area',
            'country',
            'postal_code',
            'contact_name',
            'phone_number',
        ],
        'statuses_search': [
            'id',
            'name',
            'description',
        ],
        'tags_search': [
            'id',
            'name',
            'value',
        ],
        'hypervisor_vm_assignments_search': [
            'parent_id',
            'child_id',
        ],
    }

    try:
        my_help = '[ {0} ]'.format(', '.join(sorted(terms[help_type])))
        return my_help
    except KeyError:
        LOG.error('No help terms defined for help type: {0}'.format(help_type))
        raise

def ask_yes_no(question, answer_yes=None, default='no'):
    '''Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    '''

    if answer_yes:
        sys.stdout.write(question + ' Forced yes\n')
        return True

    valid = {
        'yes': True,
        'y': True,
        'ye': True,
        'no': False,
        'n': False
    }
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def update_object_fields(args, obj_type, object_result, fields):
    '''Update object fields from CLI.'''

    LOG.debug('update_object_fields() input: {0}'.format(object_result))

    object_result.update((key.replace(obj_type + '_', ''), getattr(args, key)) for key in
                         fields if getattr(args, key, None))
    LOG.debug('update_object_fields() output: {0}'.format(object_result))

    return object_result

def print_results(args, results, default_key='name', skip_keys=None):
    '''Print results to the terminal in a yaml style output. Defaults to
    printing name and id first, but can be overridden

    Params:
        args       : arsenal.client args namespace object.
        results    : Dictionary of results to print.
        default_key: The key to use when no specific fields are asked for.
        skip_keys  : List of keys to print first. Defaults to name, id.
    '''

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
        return True

    if not skip_keys:
        skip_keys = [
            'name',
            'id',
        ]

    if args.fields:
        for res in results:
            dump = yaml.safe_dump(res, default_flow_style=False)
            for index, item in enumerate(skip_keys):
                leader = '  '
                if index == 0:
                    leader = '- '
                print('{0}{1}: {2}'.format(leader, item, res[item]))
            for line in dump.splitlines():
                skip = line.split(':')[0]
                if skip in skip_keys:
                    continue
                print('  {0}'.format(line))
            print('')

    # Default to displaying just the default_key
    else:
        for res in results:
            # Special overrides go here.
            if default_key == 'tag':
                print('{0}={1}'.format(res['name'], res['value']))
            else:
                print(res[default_key])
            if args.audit_history:
                for audit in res['audit_history']:
                    print('{0:>23} - updated_by: {1:<15} field: {2:<20} old_value: {3:<14} '
                          'new_value: {4:<14}'.format(audit['created'],
                                                      audit['updated_by'],
                                                      audit['field'],
                                                      audit['old_value'],
                                                      audit['new_value'],))

def parse_cli_args(search=None, fields=None, exact_get=None, exclude=None):
    '''Parses comma separated argument values passed from the CLI and turns them
    into a dictionary of parameters for the search() function.

    Args:
        search (str): The key=value search terms. Multiple values separated
            by comma (,). Multiple keys sparated by comma (,).
        fields (str): The specific fields to return. Multiple values separated
            by comma (,).
        exact_get (str): Whether to search for terms exactly or use wildcard
            matching.
        exclude (str): The key=value search terms to explicitly exclude. Multiple
            values separated by comma (,). Multiple keys sparated by comma (,).

    Returns:
        A dict of params to be passed to the <object_type>.search() function
    '''

    regex = re.compile(r'([^=]+)=([^=]+)(?:,|$)')
    matches = regex.findall(search)
    data = {}
    for match in matches:
        data[match[0]] = match[1]

    if exclude:
        ex_matches = regex.findall(exclude)
        for match in ex_matches:
            data['ex_{0}'.format(match[0])] = match[1]

    data['exact_get'] = exact_get
    if fields:
        data['fields'] = fields

    LOG.debug('Search data is: {0}'.format(json.dumps(data,
                                                      indent=4,
                                                      sort_keys=True)))

    return data
