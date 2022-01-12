'''Arsenal client physical_rack command line helpers.

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
    'physical_rack_oob_subnet',
    'physical_location',
    'physical_rack_server_subnet',
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
            r_names.append('{0}\n{1}'.format(res['name'],
                                             resp))
        else:
            r_names.append('{0}'.format(res['name']))

    msg = 'We are ready to update the following physical_racks: ' \
          '\n {0}\n  {1} item(s) will be updated. Continue?'.format('\n '.join(r_names),
                                                                   len(r_names))

    return msg

def process_actions(args, client, results):
    '''Process change actions for physical_racks search results.'''

    resp = None
    if args.set_tags:
        msg = _format_msg(results, args.set_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'physical_racks', results)

    if args.del_tags:
        msg = _format_msg(results, args.del_tags, mode='untag')
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'physical_racks', results)

    if any(getattr(args, key) for key in UPDATE_FIELDS):
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            for physical_rack in results:
                pd_update = update_object_fields(args,
                                                 'physical_rack',
                                                 physical_rack,
                                                 UPDATE_FIELDS)

                client.physical_racks.update(pd_update)

    return resp

def search_physical_racks(args, client):
    '''Search for physical_racks and perform optional assignment
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
    resp = client.physical_racks.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    # Allows for multiple actions to be performed at once.
    if not any(getattr(args, key) for key in action_fields):

        if args.audit_history:
            results = client.physical_racks.get_audit_history(results)

        print_results(args, results)

    else:

        resp = process_actions(args, client, results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_physical_rack(args, client):
    '''Create a new physical_rack.'''

    LOG.info('Checking if physical_rack exists name: {0} physical_location: '
             '{1}'.format(args.name, args.physical_location))

    device = {
        'name': args.name,
        'physical_location': args.physical_location,
        'oob_subnet': args.physical_rack_oob_subnet,
        'server_subnet': args.physical_rack_server_subnet,
    }

    try:

        resp = client.physical_racks.get_by_name_location(args.name,
                                                          args.physical_location)

        if ask_yes_no('Entry already exists for physical_rack name: {0}\n Would you ' \
                      'like to update it?'.format(resp['name']),
                      args.answer_yes):

            resp = client.physical_racks.update(device)
            check_resp(resp)

    except NoResultFound:
        resp = client.physical_racks.create(device)
        check_resp(resp)

def delete_physical_rack(args, client):
    '''Delete an existing physical_rack.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    results = client.physical_racks.get_by_name(args.physical_rack_name)

    if results:
        r_names = []
        for physical_racks in results:
            r_names.append(physical_racks['name'])

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n  {2} item(s) will be deleted.  Continue?'.format(args.object_type,
                                                                        '\n '.join(r_names),
                                                                        len(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for physical_rack in results:
                resp = client.physical_racks.delete(physical_rack)
                check_resp(resp)
