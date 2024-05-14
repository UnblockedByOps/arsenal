'''Arsenal client node_group command line helpers.

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
    ask_yes_no,
    check_resp,
    parse_cli_args,
    print_results,
    update_object_fields,
    )
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)


def search_node_groups(args, client):
    '''Search for node_groups and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    update_fields = [
        'node_group_owner',
        'node_group_description',
        'node_group_notes_url',
        'node_group_monitoring_contact',
        'node_group_technical_contact',
    ]
    tag_fields = [
        'set_tags',
        'del_tags',
    ]
    action_fields = update_fields + tag_fields
    search_fields = args.fields
    if any(getattr(args, key) for key in update_fields):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.node_groups.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.node_groups.get_audit_history(results)

    if not any(getattr(args, key) for key in action_fields):
        print_results(args, results)
    else:
        r_names = []

        for node_group in results:
            r_names.append('name={0},id={1}'.format(node_group['name'],
                                                    node_group['id']))

        msg = 'We are ready to update the following node_groups: \n  ' \
              '{0}\n  {1} item(s) will be updated. Continue?'.format('\n '.join(r_names), len(r_names))

        if any(getattr(args, key) for key in update_fields) and ask_yes_no(msg, args.answer_yes):
            for node_group in results:
                ng_update = update_object_fields(args,
                                                 'node_group',
                                                 node_group,
                                                 update_fields)
                client.node_groups.update(ng_update)

        if args.set_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'node_groups', results)

        if args.del_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'node_groups', results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_node_group(args, client):
    '''Create a new node_group.'''

    LOG.info('Checking if node_group name exists: {0}'.format(args.node_group_name))

    node_group = {
        'name': args.node_group_name,
        'owner': args.node_group_owner,
        'description': args.node_group_description,
        'notes_url': args.node_group_notes_url,
        'monitoring_contact': args.node_group_monitoring_contact,
        'technical_contact': args.node_group_technical_contact,
    }

    try:
        result = client.node_groups.get_by_name(args.node_group_name)

        if ask_yes_no('Entry already exists for node_group name: {0}\n Would you ' \
                      'like to update it?'.format(result['name']),
                      args.answer_yes):

            resp = client.node_groups.update(node_group)

    except NoResultFound:
        resp = client.node_groups.create(node_group)

    check_resp(resp)

def delete_node_group(args, client):
    '''Delete an existing node_group.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    try:
        result = client.node_groups.get_by_name(args.node_group_name)

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n  1 item(s) will be deleted. Continue?'.format(args.object_type, result['name'])

        if ask_yes_no(msg, args.answer_yes):
            resp = client.node_groups.delete(result)
            check_resp(resp)

    except NoResultFound:
        pass
