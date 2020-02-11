'''Arsenal client network_interface command line helpers.

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
    check_resp,
    parse_cli_args,
    print_results,
    )

LOG = logging.getLogger(__name__)


def search_network_interfaces(args, client):
    '''Search for network_interfaces.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))
    # Manual updates not allowed from the client.
    update_fields = []
    search_fields = args.fields
    if any(getattr(args, key) for key in update_fields):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.network_interfaces.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.network_interfaces.get_audit_history(results)

    if not any(getattr(args, key) for key in update_fields):
        print_results(args, results, skip_keys=['unique_id', 'id'], default_key='unique_id')
    else:
        # no direct updates allowed.
        pass

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')
