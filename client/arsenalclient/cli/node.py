'''Arsenal client node command line helpers.

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
import json

from arsenalclient.cli.common import (
    _check_tags,
    ask_yes_no,
    check_resp,
    parse_cli_args,
    print_results,
    )
from arsenalclient.authorization import check_root
from arsenalclient.version import __version__

LOG = logging.getLogger(__name__)


def _get_node_sort_order(node):
    '''Return a tuple for sorting nodes via datacenter first, then node.'''

    try:
        sort_res = (node['name'].split('.')[1], node['name'].split('.')[0])
    except IndexError:
        sort_res = ()

    return sort_res

def register(args, client):
    '''Collect all the data about a node and register it with the server'''

    client.nodes.register()

def enc(args, client):
    '''Run the External Node Classifier for puppet and return yaml.'''

    LOG.debug('Triggering node enc.')
    resp = client.nodes.enc(name=args.name, param_sources=args.inspect)
    check_resp(resp)
    results = resp['results'][0]

    print('---')
    if results['classes']:
        print('classes:')
        for my_class in results['classes']:
            print('- {0}'.format(my_class))
    else:
        print('classes: null')

    print('parameters:')
    for param in results['parameters']:
        if args.inspect:
            print('  {0}: {1} # [{2}]'.format(param,
                                              results['parameters'][param],
                                              results['param_sources'][param]))
        else:
            print('  {0}: {1}'.format(param,
                                      results['parameters'][param]))
    print('...')

def unique_id(args, client):
    '''Collect the unique_id of the current node and output it to the command
    line.'''

    if check_root():
        client.nodes.arsenal_facts.resolve()
        uid = client.nodes.get_unique_id()
        if args.json:
            res = {'unique_id': uid}
            print(json.dumps(res, indent=4, sort_keys=True))
        else:
            print(uid)

def _format_msg(results, tags=None):
    '''Format the message to be passed to ask_yes_no().'''

    r_names = []
    for node in results:
        resp = _check_tags(node, tags)
        if resp:
            r_names.append('{0}: {1}\n{2}'.format(node['name'],
                                                  node['unique_id'],
                                                  resp))
        else:
            r_names.append('{0}: {1}'.format(node['name'],
                                             node['unique_id']))

    msg = 'We are ready to update the following nodes: ' \
          '\n {0}\nContinue?'.format('\n '.join(r_names))

    return msg

def process_actions(args, client, results):
    '''Process change actions for node search results.'''

    resp = None
    if args.set_tags:
        msg = _format_msg(results, args.set_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'nodes', results)

    if args.del_tags:
        msg = _format_msg(results, args.del_tags)
        if ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'nodes', results)

    if args.set_status:
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            resp = client.statuses.assign(args.set_status, 'nodes', results)

    if args.set_node_groups:
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            for node_group_name in args.set_node_groups.split(','):
                resp = client.node_groups.assign(node_group_name, results)

    if args.del_node_groups:
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            for node_group_name in args.del_node_groups.split(','):
                resp = client.node_groups.deassign(node_group_name, results)

    if args.del_all_node_groups:
        msg = _format_msg(results)
        if ask_yes_no(msg, args.answer_yes):
            resp = client.node_groups.deassign_all(results)

    return resp

def search_nodes(args, client):
    '''Search for nodes and perform optional assignment actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    # If we are adding or deleting tags, we need existing tags for comparison.
    if args.set_tags or args.del_tags:
        if args.fields:
            args.fields += ',tags'
        else:
            args.fields = 'tags'

    params = parse_cli_args(args.search, args.fields, args.exact_get, args.exclude)
    resp = client.nodes.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    # Allows for multiple actions to be performed at once.
    if not any((args.set_tags,
                args.del_tags,
                args.set_status,
                args.set_node_groups,
                args.del_node_groups,
                args.del_all_node_groups,)):

        skip_keys = [
            'name',
            'id',
            'unique_id',
        ]

        if args.audit_history:
            results = client.nodes.get_audit_history(results)

        sort_res = sorted(results, key=_get_node_sort_order)
        print_results(args, sort_res, skip_keys=skip_keys)

    else:

        resp = process_actions(args, client, results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_node(args, client):
    '''Create a new node manually in lieu of using the register function.
    Checks if the node exists (by checking unique_id) first so it can ask
    if you want to update the existing entry. Can only update the name,
    status_id, operating_system, or hardware_profile of an existing node.
    '''

    LOG.info('Checking if unique_id exists: unique_id={0}'.format(args.unique_id))

    params = {
        'unique_id': args.unique_id,
        'exact_get': True,
    }

    resp = client.nodes.search(params)

    results = resp['results']

    node = {
        'unique_id': args.unique_id,
        'name': args.node_name,
        'status_id': args.status_id,
        'operating_system': {
            'id': args.operating_system_id,
        },
        'hardware_profile': {
            'id': args.hardware_profile_id,
        },
    }

    if results:
        if ask_yes_no('Entry already exists for unique_id: {0}: {1}\n Would you ' \
                      'like to update it?'.format(results[0]['name'], results[0]['unique_id']),
                      args.answer_yes):

            resp = client.nodes.update(node)

    else:

        resp = client.nodes.create(node)

    check_resp(resp)

def delete_nodes(args, client):
    '''Delete existing nodes. Requires a node name, id or unique_id. Since we
    enforce exact_get, only passing a name would ever possibly yeild more than
    one result.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    search = {
        'exact_get': True,
    }
    if args.node_id:
        search['id'] = args.node_id
    if args.node_name:
        search['name'] = args.node_name
    if args.unique_id:
        search['unique_id'] = args.unique_id

    resp = client.nodes.search(search)

    results = resp['results']

    if results:
        r_names = []
        for node in results:
            r_names.append('{0}: {1}'.format(node['name'], node['unique_id']))

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, '\n '.join(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for node in results:
                resp = client.nodes.delete(node)
                check_resp(resp)
