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
    ask_yes_no,
    check_resp,
    print_results,
    update_object_fields,
    )

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


def search_physical_locations(args, client):
    '''Search for physical_locations and perform optional assignment
       actions.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    action_fields = UPDATE_FIELDS + TAG_FIELDS
    search_fields = args.fields
    if any(getattr(args, key) for key in UPDATE_FIELDS):
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
        results = client.get_audit_history(results, 'physical_locations')

    if not any(getattr(args, key) for key in action_fields):
        print_results(args, results)
    else:
        r_names = []

        for physical_location in results:
            r_names.append('name={0},id={1}'.format(physical_location['name'],
                                                    physical_location['id']))

        msg = 'We are ready to update the following physical_location: \n  ' \
              '{0}\nContinue?'.format('\n '.join(r_names))

        if any(getattr(args, key) for key in UPDATE_FIELDS) and ask_yes_no(msg, args.answer_yes):
            for physical_location in results:
                dc_update = update_object_fields(args,
                                                 'physical_location',
                                                 physical_location,
                                                 UPDATE_FIELDS)

                client.physical_location_create(**dc_update)

        if args.set_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.set_tags.split(',')]
            resp = client.tag_assignments(tags, 'physical_locations', results, 'put')

        if args.del_tags and ask_yes_no(msg, args.answer_yes):
            tags = [tag for tag in args.del_tags.split(',')]
            resp = client.tag_assignments(tags, 'physical_locations', results, 'delete')

    if resp:
        check_resp(resp)
    LOG.debug('Complete.')

def create_physical_location(args, client):
    '''Create a new physical_location.'''

    LOG.info('Checking if physical_location name exists: {0}'.format(args.physical_location_name))

    resp = client.object_search(args.object_type,
                                'name={0}'.format(args.physical_location_name),
                                exact_get=True)

    results = resp['results']

    dc_fields = update_object_fields(args,
                                     'physical_location',
                                     vars(args),
                                     UPDATE_FIELDS)
    if results:
        if ask_yes_no('Entry already exists for physical_location name: {0}\n Would you ' \
                      'like to update it?'.format(results[0]['name']),
                      args.answer_yes):

            client.physical_location_create(name=args.physical_location_name,
                                      **dc_fields)

    else:
        client.physical_location_create(name=args.physical_location_name,
                                  **dc_fields)

def delete_physical_location(args, client):
    '''Delete an existing physical_location.'''

    LOG.debug('action_command is: {0}'.format(args.action_command))
    LOG.debug('object_type is: {0}'.format(args.object_type))

    search = 'name={0}'.format(args.physical_location_name)
    resp = client.object_search(args.object_type,
                                search,
                                exact_get=True)

    results = resp['results']

    if results:
        r_names = []
        for physical_locations in results:
            r_names.append(physical_locations['name'])

        msg = 'We are ready to delete the following {0}: ' \
              '\n{1}\n Continue?'.format(args.object_type, '\n '.join(r_names))

        if ask_yes_no(msg, args.answer_yes):
            for datacenter in results:
                resp = client.physical_location_delete(datacenter)
                check_resp(resp)
