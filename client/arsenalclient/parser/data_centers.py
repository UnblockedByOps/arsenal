'''Arsenal client data_centers command line parser'''
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
from arsenalclient.cli.common import date_help
from arsenalclient.cli.data_center import (
    search_data_centers,
    create_data_center,
    delete_data_center,
    )

def parser_data_centers(top_parser, otsp):
    '''Add the data_centers CLI parser.'''

    ### data_centers object_type parser (dcotp)
    dc_help = ('Perform actions on the data_centers object_type. Use the \n'
               'search action to perform assignment actions such as tagging.\n\n')
    dcotp = otsp.add_parser('data_centers',
                            description=dc_help,
                            help=dc_help,
                            parents=[top_parser])

    # data_centers action sub-parser (dcasp)
    dcasp = dcotp.add_subparsers(title='Available actions',
                                 dest='action_command')
    # data_centers search subcommand (dcssc)
    dcssc = dcasp.add_parser('search',
                             help='Search for data_center objects and optionally ' \
                             'act upon the results.',
                             parents=[top_parser])
    dcssc.add_argument('--fields',
                       '-f',
                       dest='fields',
                       help='Comma separated list of fields to display, or \'all\' for all fields.',
                       default=None)
    dcssc.add_argument('--exact',
                       action='store_true',
                       dest='exact_get',
                       default=None,
                       help='Exact match search terms.')
    dcssc.add_argument('--exclude',
                       dest='exclude',
                       default=None,
                       help='Comma separated list of key=value pairs to exclude.')
    dcssc.add_argument('-a',
                       '--audit-history',
                       action='store_true',
                       default=None,
                       help='Show audit history for search results.')

    # data_centers update action argument group (dcuaag)
    dcuaag = dcssc.add_argument_group('Update Actions')

    dcuaag.add_argument('--status',
                        dest='data_center_status',
                        help='status to assign to the search results.')

    # data_centers assignment action argument group (dcaag)
    dcaag = dcssc.add_argument_group('Assignment Actions')

    dcaag.add_argument('--tag',
                       dest='set_tags',
                       help='Comma separated list of key=value pairs to tag to ' \
                       'the search results.')
    dcaag.add_argument('--del_tag',
                       dest='del_tags',
                       help='Comma separated list of key=value pairs to un-tag from the ' \
                       'search results.')
    dcssc.add_argument('search',
                       default=None,
                       metavar='search_terms',
                       help='Comma separated list of key=value pairs to search ' \
                       'for.\n {0} \n {1}'.format(gen_help('data_centers_search'), date_help()))
    dcssc.set_defaults(func=search_data_centers)

    # data_centers create subcommand (dccsc)
    dccsc = dcasp.add_parser('create',
                             help='Create data_center objects.',
                             parents=[top_parser])

    # required data_center create argument group (rdccag)
    rdccag = dccsc.add_argument_group('required arguments')

    rdccag.add_argument('--name', '-n',
                        required=True,
                        dest='data_center_name',
                        help='data_center_name to create.')
    rdccag.add_argument('--status', '-s',
                        dest='data_center_status',
                        help='data_center_status to set the new data_center to. ' \
                        'If not specified will be set to setup.')
    rdccag.set_defaults(func=create_data_center)

    # data_centers delete subcommand (dcdsc)
    dcdsc = dcasp.add_parser('delete',
                             help='Delete data_center objects.',
                             parents=[top_parser])

    # required data_center delete argument group (rdcdag)
    rdcdag = dcdsc.add_argument_group('required arguments')

    rdcdag.add_argument('--name', '-n',
                        required=True,
                        dest='data_center_name',
                        help='data_center_name to delete.')
    dcdsc.set_defaults(func=delete_data_center)

    return top_parser, otsp
