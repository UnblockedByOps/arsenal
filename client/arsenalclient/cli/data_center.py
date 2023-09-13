'''Arsenal client data_center command line helpers.

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
    )
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)
UPDATE_FIELDS = [
    'data_center_status',
]
TAG_FIELDS = [
    'set_tags',
    'del_tags',
]


def search_data_centers(args, client):
    '''Search for data_centers and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    action_fields = UPDATE_FIELDS + TAG_FIELDS
    search_fields = args.fields
    if any(getattr(args, key) for key in UPDATE_FIELDS):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.data_centers.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.data_centers.get_audit_history(results)

    if not any(getattr(args, key) for key in action_fields):
        print_results(args, results)
    else:
        r_names = []

        for data_center in results:
            r_names.append('name={0},id={1}'.format(data_center['name'],
                                                    data_center['id']))

        msg = 'We are ready to update the following data_center: \n  ' \
              '{0}\n  {1} item(s) will be updated. Continue?'.format('\n '.join(r_names), len(r_names))

        if args.data_center_status and ask_yes_no(msg, args.answer_yes):
            resp = client.statuses.assign(args.data_center_status, 'data_centers', results)

        if args.set_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.assign(name, value, 'data_centers', results)

        if args.del_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            for tag in tags:
                name, value = tag.split('=')
                resp = client.tags.deassign(name, value, 'data_centers', results)

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_data_center(args, client):
    '''Create a new data_center.'''


    LOG.info('Checking if data_center name exists: {0}'.format(args.data_center_name))

    data_center = {
        'name': args.data_center_name,
        'status': args.data_center_status,
    }

    try:
        result = client.data_centers.get_by_name(args.data_center_name)

        if ask_yes_no('Entry already exists for data_center name: {0}\n Would you ' \
                      'like to update it?'.format(result['name']),
                      args.answer_yes):

            resp = client.data_centers.update(data_center)

    except NoResultFound:
        resp = client.data_centers.create(data_center)

    check_resp(resp)

def delete_data_center(args, client):
    '''Delete an existing data_center.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    try:
        params = {
            'name': args.data_center_name,
            'exact_get': True,
        }
        resp = client.data_centers.search(params)

        results = resp['results']

        r_names = []
        for data_centers in results:
            r_names.append(data_centers['name'])

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n  {2} item(s) will be deleted.  Continue?'.format(args.object_type,
                                                                        '\n '.join(r_names),
                                                                        len(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for datacenter in results:
                resp = client.data_centers.delete(datacenter)
                check_resp(resp)
    except NoResultFound:
        LOG.info('data_center not found, nothing to do.')
