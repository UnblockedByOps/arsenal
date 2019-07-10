'''Arsenal client physical_devices command line parser'''
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
from arsenalclient.cli.physical_device import (
    search_physical_devices,
    create_physical_device,
    delete_physical_device,
    )

def parser_physical_devices(top_parser, otsp):
    '''Add the physical_devices CLI parser.'''

    ### physical_devices object_type parser (otp)
    my_help = ('Perform actions on the physical_devices object_type. Use the \n'
               'search action to perform assignment actions such as tagging (TBD).\n\n')
    otp = otsp.add_parser('physical_devices',
                          description=my_help,
                          help=my_help,
                          parents=[top_parser])

    # physical_devices action sub-parser (asp)
    asp = otp.add_subparsers(title='Available actions',
                             dest='action_command')
    # physical_devices search subcommand (ssc)
    ssc = asp.add_parser('search',
                         help='Search for physical_device objects and optionally ' \
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

    # physical_devices update action argument group (uaag)
    uaag = ssc.add_argument_group('Update Actions')

    uaag.add_argument('-e',
                      '--elevation-id',
                      dest='physical_device_elevation_id',
                      help='Update physical_device elevation_id.')
    uaag.add_argument('-H',
                      '--hardware-profile-id',
                      dest='physical_device_hardware_profile_id',
                      help='Update physical_device hardware_profile_id.')
    uaag.add_argument('-i',
                      '--oob-ip-address',
                      dest='physical_device_oob_ip_address',
                      help='Update physical_device oob_ip_address.')
    uaag.add_argument('-l',
                      '--location-id',
                      dest='physical_device_location_id',
                      help='Update physical_device location_id.')
    uaag.add_argument('-m',
                      '--oob-mac-address',
                      dest='physical_device_oob_mac_address',
                      help='Update physical_device oob_mac_address.')
    uaag.add_argument('-r',
                      '--rack-id',
                      dest='physical_device_rack_id',
                      help='Update physical_device rack_id.')

    # physical_devices assignment action argument group (aag)
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
                     'for.\n {0}'.format(gen_help('physical_devices_search')))
    ssc.set_defaults(func=search_physical_devices)

    # physical_devices create subcommand (csc)
    csc = asp.add_parser('create',
                         help='Create physical_device objects.',
                         parents=[top_parser])

    # required physical_device create argument group (rcag)
    rcag = csc.add_argument_group('required arguments')

    rcag.add_argument('-s',
                      '--serial-number',
                      required=True,
                      dest='physical_device_serial_number',
                      help='physical_device_serial_number to create.')
    rcag.set_defaults(func=create_physical_device)

    # physical_devices delete subcommand (dsc)
    dsc = asp.add_parser('delete',
                         help='Delete physical_device objects.',
                         parents=[top_parser])

    # required physical_device delete argument group (rdag)
    rdag = dsc.add_argument_group('required arguments')

    rdag.add_argument('-s',
                      '--serial-number',
                      required=True,
                      dest='physical_device_serial_number',
                      help='physical_device_serial_number to delete.')
    dsc.set_defaults(func=delete_physical_device)

    return top_parser, otsp
