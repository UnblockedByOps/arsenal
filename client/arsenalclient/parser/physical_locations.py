'''Arsenal client physical_locations command line parser'''
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
from arsenalclient.cli.common import gen_help
from arsenalclient.cli.physical_location import (
    search_physical_locations,
    create_physical_location,
    delete_physical_location,
    )

def parser_physical_locations(top_parser, otsp):
    '''Add the physical_locations CLI parser.'''

    ### physical_locations object_type parser (otp)
    my_help = ('Perform actions on the physical_locations object_type. Use the \n'
               'search action to perform assignment actions such as tagging (TBD).\n\n')
    otp = otsp.add_parser('physical_locations',
                          description=my_help,
                          help=my_help,
                          parents=[top_parser])

    # physical_locations action sub-parser (asp)
    asp = otp.add_subparsers(title='Available actions',
                             dest='action_command')
    # physical_locations search subcommand (ssc)
    ssc = asp.add_parser('search',
                         help='Search for physical_location objects and optionally ' \
                         'act upon the results.',
                         parents=[top_parser])
    ssc.add_argument('--fields',
                     '-f',
                     dest='fields',
                     help='Comma separated list of fields to display, or \'all\' for all fields.',
                     default=None)
    ssc.add_argument('--exact',
                     action='store_true',
                     dest='exact_get',
                     default=None,
                     help='Exact match search terms.')
    ssc.add_argument('--exclude',
                     dest='exclude',
                     default=None,
                     help='Comma separated list of key=value pairs to exclude.')
    ssc.add_argument('-a',
                     '--audit-history',
                     action='store_true',
                     default=None,
                     help='Show audit history for search results.')

    # physical_locations update action argument group (uaag)
    uaag = ssc.add_argument_group('Update Actions')

    uaag.add_argument('--name', '-n',
                      dest='physical_location_name',
                      help='physical_location_name to create.')
    uaag.add_argument('-a1',
                      '--address-1',
                      dest='physical_location_address_1',
                      help='Update physical_location address 1.')
    uaag.add_argument('-a2',
                      '--address-2',
                      dest='physical_location_address_2',
                      help='Update physical_location address 2.')
    uaag.add_argument('-c',
                      '--city',
                      dest='physical_location_city',
                      help='Update physical_location city.')
    uaag.add_argument('-s',
                      '--state',
                      dest='physical_location_admin_area',
                      help='Update physical_location state.')
    uaag.add_argument('--status',
                      dest='physical_location_status',
                      help='status to assign to the search results.')
    uaag.add_argument('-t',
                      '--contact-name',
                      dest='physical_location_contact_name',
                      help='Update physical_location contact name.')
    uaag.add_argument('-C',
                      '--country',
                      dest='physical_location_country',
                      help='Update physical_location country.')
    uaag.add_argument('-P',
                      '--phone-number',
                      dest='physical_location_phone_number',
                      help='Update physical_location contact phone number.')
    uaag.add_argument('-p',
                      '--postal-code',
                      dest='physical_location_postal_code',
                      help='Update physical_location postal code.')
    uaag.add_argument('-r',
                      '--provider',
                      dest='physical_location_provider',
                      help='Update physical_location provider.')

    # physical_locations assignment action argument group (aag)
    aag = ssc.add_argument_group('Assignment Actions')

    aag.add_argument('--tag',
                     dest='set_tags',
                     help='Comma separated list of key=value pairs to tag to ' \
                     'the search results.')
    aag.add_argument('--del_tag',
                     dest='del_tags',
                     help='Comma separated list of key=value pairs to un-tag from the ' \
                     'search results.')
    ssc.add_argument('search',
                     default=None,
                     metavar='search_terms',
                     help='Comma separated list of key=value pairs to search ' \
                     'for.\n {0}'.format(gen_help('physical_locations_search')))
    ssc.set_defaults(func=search_physical_locations)

    # physical_locations create subcommand (csc)
    csc = asp.add_parser('create',
                         help='Create physical_location objects.',
                         parents=[top_parser])

    # required physical_location create argument group (rcag)
    rcag = csc.add_argument_group('required arguments')

    rcag.add_argument('--name', '-n',
                      required=True,
                      dest='physical_location_name',
                      help='physical_location_name to create.')
    rcag.add_argument('-a1',
                      '--address-1',
                      dest='physical_location_address_1',
                      help='Update physical_location address 1.')
    rcag.add_argument('-a2',
                      '--address-2',
                      dest='physical_location_address_2',
                      help='Update physical_location address 2.')
    rcag.add_argument('-c',
                      '--city',
                      dest='physical_location_city',
                      help='Update physical_location city.')
    rcag.add_argument('-s',
                      '--state',
                      dest='physical_location_admin_area',
                      help='Update physical_location state.')
    rcag.add_argument('--status',
                      dest='physical_location_status',
                      help='status to assign to the search results.')
    rcag.add_argument('-t',
                      '--contact-name',
                      dest='physical_location_contact_name',
                      help='Update physical_location contact name.')
    rcag.add_argument('-C',
                      '--country',
                      dest='physical_location_country',
                      help='Update physical_location country.')
    rcag.add_argument('-P',
                      '--phone-number',
                      dest='physical_location_phone_number',
                      help='Update physical_location contact phone number.')
    rcag.add_argument('-p',
                      '--postal-code',
                      dest='physical_location_postal_code',
                      help='Update physical_location postal code.')
    rcag.add_argument('-r',
                      '--provider',
                      dest='physical_location_provider',
                      help='Update physical_location provider.')

    rcag.set_defaults(func=create_physical_location)

    # physical_locations delete subcommand (dsc)
    dsc = asp.add_parser('delete',
                         help='Delete physical_location objects.',
                         parents=[top_parser])

    # required physical_location delete argument group (rdag)
    rdag = dsc.add_argument_group('required arguments')

    rdag.add_argument('--name', '-n',
                      required=True,
                      dest='physical_location_name',
                      help='physical_location_name to delete.')
    dsc.set_defaults(func=delete_physical_location)

    return top_parser, otsp
