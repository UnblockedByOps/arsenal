'''Arsenal client physical_device command line helpers.

These functions are called directly by args.func() to invoke the
appropriate action. They also handle output formatting to the commmand
line.

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
import logging
import sys
import csv
import json
from arsenalclient.cli.common import (
    _check_tags,
    ask_yes_no,
    check_resp,
    parse_cli_args,
    print_results,
    update_object_fields,
    )
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)
UPDATE_FIELDS = [
    'hardware_profile',
    'mac_address_1',
    'mac_address_2',
    'oob_ip_address',
    'oob_mac_address',
    'physical_device_status',
    'physical_elevation',
    'physical_location',
    'physical_rack',
]
TAG_FIELDS = [
    'set_tags',
    'del_tags',
]

def _format_msg(results, tags=None, mode='tag'):
    '''Format the message to be passed to ask_yes_no().'''

    r_names = []
    for res in results:
        resp = _check_tags(res, tags, mode=mode)
        if resp:
            r_names.append('{0}\n{1}'.format(res['serial_number'],
                                             resp))
        else:
            r_names.append('{0}'.format(res['serial_number']))

    msg = 'We are ready to update the following physical_devices: ' \
          '\n {0}\nContinue?'.format('\n '.join(r_names))

    return msg

def process_actions(args, client, results):
    '''Process change actions for physical_devices search results.'''

    resp = None
    if args.set_tags:
        msg = _format_msg(results, args.set_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'physical_devices', results)

    if args.del_tags:
        msg = _format_msg(results, args.del_tags, mode='untag')
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'physical_devices', results)

    # Status is special becasue it is updated via the statuses class.
    if args.physical_device_status:
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            resp = client.statuses.assign(args.physical_device_status, 'physical_devices', results)
            # Remove the param form the list so it doesn't try to update it
            # again and fail.
            UPDATE_FIELDS.remove('physical_device_status')

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            for physical_device in results:
                pd_update = update_object_fields(args,
                                                 'physical_device',
                                                 physical_device,
                                                 UPDATE_FIELDS)

                client.physical_devices.update(pd_update)

    return resp

def search_physical_devices(args, client):
    '''Search for physical_devices and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    action_fields = UPDATE_FIELDS + TAG_FIELDS
    search_fields = args.fields

    # If we are adding or deleting tags, we need existing tags for comparison.
    if args.set_tags or args.del_tags:
        if search_fields:
            search_fields += ',tags'
        else:
            search_fields = 'tags'

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.physical_devices.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    # Allows for multiple actions to be performed at once.
    if not any(getattr(args, key) for key in action_fields):

        if args.audit_history:
            results = client.physical_devices.get_audit_history(results)

        print_results(args, results, default_key='serial_number', first_keys=['serial_number', 'id'])

    else:

        resp = process_actions(args, client, results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def tag_physical_device_import(client, set_tags, results):
    '''Tag a physical device that is newly created by the import tool with any
    tags that were provided in the csv file.'''

    tags = [tag for tag in set_tags.split('|')]
    for tag in tags:
        name, value = tag.split('=')
        resp = client.tags.assign(name, value, 'physical_devices', results)
        LOG.debug('Tag response: {0}'.format(resp))

def create_physical_device(args, client, device=None):
    '''Create a new physical_device.'''

    try:
        serial_number = device['serial_number']
        import_tool = True
    except TypeError:
        import_tool = False
        serial_number = args.serial_number

        device = {
            'hardware_profile': args.hardware_profile,
            'mac_address_1': args.mac_address_1,
            'mac_address_2': args.mac_address_2,
            'oob_ip_address': args.oob_ip_address,
            'oob_mac_address': args.oob_mac_address,
            'physical_elevation': args.physical_elevation,
            'physical_location': args.physical_location,
            'physical_rack': args.physical_rack,
            'serial_number': args.serial_number,
        }

    LOG.info('Checking if physical_device serial_number exists: {0}'.format(serial_number))

    try:

        resp = client.physical_devices.get_by_serial_number(serial_number)

        if ask_yes_no('Entry already exists for physical_device name: {0}\n Would you ' \
                      'like to update it?'.format(resp['serial_number']),
                      args.answer_yes):

            resp = client.physical_devices.update(device)
            LOG.debug('Update response is: {0}'.format(resp))
            if import_tool:
                try:
                    set_tags = device['tags']
                    tag_physical_device_import(client, set_tags, resp['results'])
                except KeyError:
                    pass
                return resp
            else:
                return check_resp(resp)

    except NoResultFound:
        resp = client.physical_devices.create(device)
        LOG.debug('Create response is: {0}'.format(resp))
        if import_tool:
            try:
                set_tags = device['tags']
                tag_physical_device_import(client, set_tags, resp['results'])
            except KeyError:
                pass
            return resp
        else:
            return check_resp(resp)

def delete_physical_device(args, client):
    '''Delete an existing physical_device.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    try:
        results = client.physical_devices.get_by_serial_number(args.physical_device_serial_number)

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, results['serial_number'])

        if ask_yes_no(msg, args.answer_yes):
            resp = client.physical_devices.delete(results)
            check_resp(resp)
    except NoResultFound:
        LOG.info('Nothing to do.')

def import_physical_device(args, client):
    '''Import physical_devices from a csv file.'''

    LOG.info('Beginning physical_device import from file: {0}'.format(args.physical_device_import))
    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    failures = []
    overall_exit = 0
    try:
        with open(args.physical_device_import) as csv_file:
            field_names = [
                'serial_number',
                'physical_location',
                'physical_rack',
                'physical_elevation',
                'mac_address_1',
                'mac_address_2',
                'hardware_profile',
                'oob_ip_address',
                'oob_mac_address',
                'tags',
                'status',
            ]
            device_import = csv.DictReader(csv_file, delimiter=',', fieldnames=field_names)
            for count, row in enumerate(device_import):
                if row['serial_number'].startswith('#'):
                    continue
                LOG.info('Processing row: {0}...'.format(count))

                row = check_null_fields(row, field_names)
                LOG.debug(json.dumps(row, indent=4, sort_keys=True))

                resp = create_physical_device(args, client, device=row)
                LOG.debug(json.dumps(resp, indent=4, sort_keys=True))

                if not resp:
                    continue

                if resp['http_status']['code'] != 200:
                    resp['http_status']['row'] = row
                    resp['http_status']['row_number'] = count
                    failures.append(resp['http_status'])

        if failures:
            overall_exit = 1
            LOG.error('The following rows were unable to be processed:')
            for fail in failures:
                LOG.error('    Row: {0} Data: {1} Error: {2}'.format(fail['row_number'],
                                                                     fail['row'],
                                                                     fail['message'],))

        LOG.info('physical_device import complete')
        sys.exit(overall_exit)

    except IOError as ex:
        LOG.error(ex)

def export_check_optional(param):
    '''Checks if an optional param exists or not during export. Sets to empty
    string if not, otherwise returns the param as-is.'''

    if not param or param == 'None':
        return ''
    return param

def export_physical_device(args, client):
    '''Export physical_devices to standard out or a csv file.'''

    LOG.info('Beginning physical_device export...')

    params = parse_cli_args(args.search, 'all')
    if 'physical_location.name' not in params:
        LOG.error('physical_location.name search parameter is required')
        sys.exit(1)
    resp = client.physical_devices.search(params)
    if not resp['results']:
        return

    LOG.info('Found {0} device(s).'.format(resp['meta']['total']))
    LOG.debug(json.dumps(resp, indent=4, sort_keys=True))

    all_results = []
    for result in resp['results']:

        my_device = [
            result['serial_number'],
            result['physical_location']['name'],
            result['physical_rack']['name'],
            str(result['physical_elevation']['elevation']),
            result['mac_address_1'],
            export_check_optional(result['mac_address_2']),
            export_check_optional(result['hardware_profile']['name']),
            result['oob_ip_address'],
            result['oob_mac_address'],
        ]
        joined_tags = ''
        for tag in result['tags']:
            joined_tags += '{0}={1}|'.format(tag['name'], tag['value'])
        joined_tags = joined_tags.rstrip('|')
        if joined_tags:
            my_device.append(joined_tags)

        line = ','.join(my_device)
        if args.export_csv:
            all_results.append(line)
        else:
            print(line)

    if all_results:
        LOG.info('Writing results to csv: {0}'.format(args.export_csv))

        with open(args.export_csv, 'w') as the_file:
            for result in all_results:
                the_file.write('{0}\n'.format(result))

def check_null_fields(row, field_names):
    '''Checks for keys will null values and removes them. This allows the API
    to return appropriate errors for keys that require a value.'''

    for key in field_names:
        if not row[key]:
            del row[key]
    return row
