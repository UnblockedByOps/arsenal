'''Arsenal client network_interfaces command line parser'''
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
from arsenalclient.cli.network_interface import (
    search_network_interfaces,
    )

def parser_network_interfaces(top_parser, otsp):
    '''Add the network_interfaces CLI parser.'''

    ### network_interfaces object_type parser (niotp)
    ni_help = ('Perform actions on the network_interfaces object_type.\n'
               'Currently only searching is supported.\n\n')
    niotp = otsp.add_parser('network_interfaces',
                            description=ni_help,
                            help=ni_help,
                            parents=[top_parser])

    # network_interfaces action sub-parser (niasp)
    niasp = niotp.add_subparsers(title='Actions',
                                 dest='action_command')

    # network_interfaces search subcommand (nissc)
    nissc = niasp.add_parser('search',
                             help='Search for network_interface objects.',
                             parents=[top_parser])
    nissc.add_argument('--fields',
                       '-f',
                       dest='fields',
                       help='Comma separated list of fields to display, or \'all\' for all fields.',
                       default=None)
    nissc.add_argument('--exact',
                       action='store_true',
                       dest='exact_get',
                       default=None,
                       help='Exact match search terms.')
    nissc.add_argument('--exclude',
                       dest='exclude',
                       default=None,
                       help='Comma separated list of key=value pairs to exclude.')
    nissc.add_argument('-a',
                       '--audit-history',
                       action='store_true',
                       default=None,
                       help='Show audit history for search results.')
    nissc.add_argument('search',
                       default=None,
                       metavar='search_terms',
                       help='Comma separated list of key=value pairs to search ' \
                            'for.\n {0}'.format(gen_help('network_interfaces_search')))
    nissc.set_defaults(func=search_network_interfaces)

    return top_parser, otsp
