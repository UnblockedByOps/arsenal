'''Arsenal client physical_location command line helpers.

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
    'physical_location_address_1',
    'physical_location_address_2',
    'physical_location_admin_area',
    'physical_location_city',
    'physical_location_contact_name',
    'physical_location_country',
    'physical_location_phone_number',
    'physical_location_postal_code',
    'physical_location_provider',
]
TAG_FIELDS = [
    'set_tags',
    'del_tags',
]

def _format_msg(results, tags=None):
    '''Format the message to be passed to ask_yes_no().'''

    r_names = []
    for loc in results:
        resp = _check_tags(loc, tags)
        if resp:
            r_names.append('{0}: {1}\n{2}'.format(loc['name'],
                                                  loc['id'],
                                                  resp))
        else:
            r_names.append('{0}: {1}'.format(loc['name'],
                                             loc['id']))

    msg = 'We are ready to update the following physical_locations: ' \
          '\n {0}\nContinue?'.format('\n '.join(r_names))

    return msg

def process_actions(args, client, results):
    '''Process change actions for physical_locations search results.'''

    resp = None
    if args.set_tags:
        msg = _format_msg(results, args.set_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'physical_locations', results)

    if args.del_tags:
        msg = _format_msg(results, args.del_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'physical_locations', results)

    return resp

def search_physical_locations(args, client):
    '''Search for physical_locations and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    action_fields = UPDATE_FIELDS + TAG_FIELDS
    search_fields = args.fields

    # If we are adding or deleting tags, we need existing tags for comparison.
    if args.set_tags or args.del_tags:
        if args.fields:
            args.fields += ',tags'
        else:
            args.fields = 'tags'

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.physical_locations.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    # Allows for multiple actions to be performed at once.
    if not any(getattr(args, key) for key in action_fields):

        if args.audit_history:
            results = client.physical_locations.get_audit_history(results)

        print_results(args, results)

    else:

        resp = process_actions(args, client, results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_physical_location(args, client):
    '''Create a new physical_location.'''

    LOG.info('Checking if physical_location name exists: {0}'.format(args.physical_location_name))

    try:
        resp = client.physical_locations.get_by_name(args.physical_location_name)

        loc_fields = update_object_fields(args,
                                          'physical_location',
                                          vars(args),
                                          UPDATE_FIELDS)

        if ask_yes_no('Entry already exists for physical_location name: {0}\n Would you ' \
                      'like to update it?'.format(resp['name']),
                      args.answer_yes):

            client.physical_locations.update(name=args.physical_location_name,
                                             **loc_fields)

    except NoResultFound:
        client.physical_locations.create(name=args.physical_location_name,
                                         **loc_fields)

def delete_physical_location(args, client):
    '''Delete an existing physical_location.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    results = client.physical_locations.get_by_name(args.physical_location_name)

    if results:
        r_names = []
        for physical_locations in results:
            r_names.append(physical_locations['name'])

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, '\n '.join(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for physical_location in results:
                resp = client.physical_locations.delete(physical_location)
                check_resp(resp)
