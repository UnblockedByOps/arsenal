'''Arsenal client status command line helpers.

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
    update_object_fields,
    print_results,
    )

LOG = logging.getLogger(__name__)


def search_statuses(args, client):
    '''Search for statuses and perform optional updates. '''
    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))
    update_fields = [
        'statuses_description',
    ]
    search_fields = args.fields
    if any(getattr(args, key) for key in update_fields):
        search_fields = 'all'

    resp = None
    resp = client.object_search(args.object_type,
                                args.search,
                                fields=search_fields,
                                exact_get=args.exact_get,
                                exclude=args.exclude)

    if not resp.get('results'):
        return resp

    results = resp['results']

    if args.audit_history:
        results = client.get_audit_history(results, 'statuses')

    if not any(getattr(args, key) for key in update_fields):
        print_results(args, results)
    else:
        if len(results) > 1:
            LOG.error('Expected 1 result, exiting.')
            sys.exit(1)
        else:
            status = results[0]
        LOG.debug('STATUS: {0}'.format(status))
        msg = 'We are ready to update the following status: \n  ' \
              '{0}\nContinue?'.format(status['name'])
        if any(getattr(args, key) for key in update_fields) and ask_yes_no(msg, args.answer_yes):
            status_update = update_object_fields(args,
                                                 'statuses',
                                                 status,
                                                 update_fields)
            resp = client.status_create(**status_update)
    if resp:
        check_resp(resp)
    LOG.debug('Complete.')
