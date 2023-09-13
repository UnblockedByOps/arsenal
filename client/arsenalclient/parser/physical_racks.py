'''Arsenal client physical_racks command line parser'''
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
import sys
from argparse import RawTextHelpFormatter
from arsenalclient.cli.common import gen_help
from arsenalclient.cli.common import date_help
from arsenalclient.cli.physical_rack import (
    search_physical_racks,
    create_physical_rack,
    delete_physical_rack,
    )

def parser_physical_racks(top_parser, otsp):
    '''Add the physical_racks CLI parser.'''

    ### physical_racks object_type parser (otp)
    my_help = ('Perform actions on the physical_racks object_type. Use the \n'
               'search action to perform assignment actions such as tagging (TBD).\n\n')
    otp = otsp.add_parser('physical_racks',
                          description=my_help,
                          help=my_help,
                          parents=[top_parser])

    # physical_racks action sub-parser (asp)
    # https://bugs.python.org/issue16308
    if sys.version_info.major == 2 or sys.version_info.minor < 7:
        asp = otp.add_subparsers(title='Available actions',
                                 dest='action_command')
    else:
        asp = otp.add_subparsers(title='Available actions',
                                 dest='action_command',
                                 required=True)

    # physical_racks search subcommand (ssc)
    ssc = asp.add_parser('search',
                         help='Search for physical_rack objects and optionally ' \
                         'act upon the results.',
                         parents=[top_parser],
                         formatter_class=RawTextHelpFormatter)
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

    # physical_racks update action argument group (uaag)
    uaag = ssc.add_argument_group('Update Actions')

    uaag.add_argument('-l',
                      '--location',
                      dest='physical_location',
                      help='Update physical_rack location.')
    uaag.add_argument('-o',
                      '--oob-subnet',
                     dest='physical_rack_oob_subnet',
                      help='Update the oob-subnet (must be CIDR notation).')
    uaag.add_argument('-s',
                      '--server-subnet',
                     dest='physical_rack_server_subnet',
                      help='Update the server-subnet (must be CIDR notation).')

    # physical_racks assignment action argument group (aag)
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
                          'for:\n{0} \n {1}'.format(gen_help('physical_racks_search'),
                                                    date_help()))
    ssc.set_defaults(func=search_physical_racks)

    # physical_racks create subcommand (csc)
    csc = asp.add_parser('create',
                         help='Create physical_rack objects.',
                         parents=[top_parser])

    csc.add_argument('-o',
                     '--oob-subnet',
                     dest='physical_rack_oob_subnet',
                     help='the oob-subnet (must be CIDR notation).')

    csc.add_argument('-s',
                     '--server-subnet',
                     dest='physical_rack_server_subnet',
                     help='the oob-subnet (must be CIDR notation).')

    # required physical_rack create argument group (rcag)
    rcag = csc.add_argument_group('required arguments')

    rcag.add_argument('-l',
                      '--location',
                      dest='physical_location',
                      required=True,
                      help='The physical rack location name.')
    rcag.add_argument('-n',
                      '--name',
                      required=True,
                      help='The physical rack name.')

    rcag.set_defaults(func=create_physical_rack)

    # physical_racks delete subcommand (dsc)
    dsc = asp.add_parser('delete',
                         help='Delete physical_rack objects.',
                         parents=[top_parser])

    # required physical_rack delete argument group (rdag)
    rdag = dsc.add_argument_group('required arguments')

    rdag.add_argument('-n',
                      '--name',
                      required=True,
                      dest='physical_rack_name',
                      help='physical_rack_name to delete.')
    dsc.set_defaults(func=delete_physical_rack)

    return top_parser, otsp
