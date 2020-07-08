'''Arsenal client tag command line helpers.

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

LOG = logging.getLogger(__name__)


def search_tags(args, client):
    '''Search for tags and perform optional assignment actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    params = parse_cli_args(args.search, args.fields, args.exact_get, args.exclude)
    resp = client.tags.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.tags.get_audit_history(results)

    # switch to any if there's more than one
    if not args.set_tags:

        first_keys = [
            'name',
            'value',
        ]
        print_results(args, results, first_keys=first_keys, default_key='tag')

    else:
        LOG.info('Assigning tags via tag search is not implemented.')

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_tag(args, client):
    '''Create a new tag.'''

    params = {
        'name': args.tag_name,
        'value': args.tag_value,
    }

    client.tags.create(params)

def delete_tag(args, client):
    '''Delete an existing tag. Requires a tag name and value.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    search = {
        'name': args.tag_name,
        'value': args.tag_value,
        'exact_get': True,
    }

    resp = client.tags.search(search)

    results = resp['results']

    if results:
        r_names = []
        for tag in results:
            r_names.append('{0}={1}'.format(tag['name'], tag['value']))

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, '\n '.join(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for tag in results:
                resp = client.tags.delete(tag)
                check_resp(resp)
