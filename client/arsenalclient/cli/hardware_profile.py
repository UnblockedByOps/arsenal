'''Arsenal client hardware_profile command line helpers.

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
import sys
import logging
from arsenalclient.cli.common import (
    ask_yes_no,
    check_resp,
    parse_cli_args,
    print_results,
    update_object_fields,
    )

LOG = logging.getLogger(__name__)


def search_hardware_profiles(args, client):
    '''Search for hardware_profiles and perform optional updates.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    resp = None

    update_fields = [
        'hardware_profiles_rack_color',
        'hardware_profiles_rack_u',
    ]

    search_fields = args.fields
    if any(getattr(args, key) for key in update_fields):
        search_fields = 'all'

    params = parse_cli_args(args.search, search_fields, args.exact_get, args.exclude)
    resp = client.hardware_profiles.search(params)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.hardware_profiles.get_audit_history(results)

    if not any(getattr(args, key) for key in update_fields):
        print_results(args, results)
    else:
        if len(results) > 1:
            LOG.error('Expected 1 result, exiting.')
            sys.exit(1)
        else:
            hardware_profile = results[0]
        LOG.debug('HARDWARE_PROFILE: {0}'.format(hardware_profile))
        msg = 'We are ready to update the following hardware_profile: \n  ' \
              '{0}\n  1 item(s) will be updated. Continue?'.format(hardware_profile['name'])
        if any(getattr(args, key) for key in update_fields) and ask_yes_no(msg, args.answer_yes):
            hardware_profile_update = update_object_fields(args,
                                                           'hardware_profiles',
                                                           hardware_profile,
                                                           update_fields)
            resp = client.hardware_profiles.update(hardware_profile_update)
    if resp:
        check_resp(resp)
    LOG.debug('Complete.')
