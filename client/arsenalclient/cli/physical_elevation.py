'''Arsenal client physical_elevation command line helpers.

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
    'physical_location',
    'physical_rack',
]

def _format_msg(results, tags=None, mode='tag'):
    '''Format the message to be passed to ask_yes_no().'''

    r_names = []
    for res in results:
        resp = _check_tags(res, tags, mode=mode)
        if resp:
            r_names.append('{0}\n{1}'.format(res['name'],
                                             resp))
        else:
            r_names.append('{0}'.format(res['name']))

    msg = 'We are ready to update the following physical_elevations: ' \
          '\n {0}\nContinue?'.format('\n '.join(r_names))

    return msg

def process_actions(args, client, results):
    '''Process change actions for physical_elevations search results.'''

    resp = None

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            for physical_elevation in results:
                pd_update = update_object_fields(args,
                                                 'physical_elevation',
                                                 physical_elevation,
                                                 UPDATE_FIELDS)

                client.physical_elevations.update(pd_update)

    return resp

def search_physical_elevations(args, client):
    '''Search for physical_elevations and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    action_fields = UPDATE_FIELDS
    search_fields = args.fields

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.physical_elevations.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    # Allows for multiple actions to be performed at once.
    if not any(getattr(args, key) for key in action_fields):

        if args.audit_history:
            results = client.physical_elevations.get_audit_history(results)

        print_results(args, results, default_key='elevation',
                      first_keys=['elevation', 'id'])

    else:

        resp = process_actions(args, client, results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_physical_elevation(args, client):
    '''Create a new physical_elevation.'''

    LOG.info('Checking if physical_elevation name exists: {0}'.format(args.physical_elevation))

    device = {
        'elevation': args.physical_elevation,
        'physical_location': args.physical_location,
        'physical_rack': args.physical_rack,
    }

    try:

        resp = client.physical_elevations.get_by_loc_rack_el(args.physical_location,
                                                             args.physical_rack,
                                                             args.physical_elevation)

        if ask_yes_no('Entry already exists for physical_elevation name: {0}\n Would you ' \
                      'like to update it?'.format(resp['name']),
                      args.answer_yes):

            resp = client.physical_elevations.update(device)
            check_resp(resp)

    except NoResultFound:
        resp = client.physical_elevations.create(device)
        check_resp(resp)

def delete_physical_elevation(args, client):
    '''Delete an existing physical_elevation.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    results = client.physical_elevations.get_by_name(args.physical_elevation_name)

    if results:
        r_names = []
        for physical_elevations in results:
            r_names.append(physical_elevations['name'])

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, '\n '.join(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for physical_elevation in results:
                resp = client.physical_elevations.delete(physical_elevation)
                check_resp(resp)
