'''Arsenal client ip_addresses command line parser'''
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
from arsenalclient.cli.ip_address import (
    search_ip_addresses,
    )

def parser_ip_addresses(top_parser, otsp):
    '''Add the ip_addresses CLI parser.'''

    ### ip_addresses object_type parser (iaotp)
    ia_help = ('Perform actions on the ip_addresses object_type.\n'
               'Currently only searching is supported.\n\n')
    iaotp = otsp.add_parser('ip_addresses',
                            description=ia_help,
                            help=ia_help,
                            parents=[top_parser])

    # ip_addresses action sub-parser (iaasp)
    iaasp = iaotp.add_subparsers(title='Actions',
                                 dest='action_command')

    # ip_addresses search subcommand (iassc)
    iassc = iaasp.add_parser('search',
                             help='Search for ip_address objects.',
                             parents=[top_parser])
    iassc.add_argument('--fields',
                       '-f',
                       dest='fields',
                       help='Comma separated list of fields to display, or \'all\' for all fields.',
                       default=None)
    iassc.add_argument('--exact',
                       action='store_true',
                       dest='exact_get',
                       default=None,
                       help='Exact match search terms.')
    iassc.add_argument('--exclude',
                       dest='exclude',
                       default=None,
                       help='Comma separated list of key=value pairs to exclude.')
    iassc.add_argument('-a',
                       '--audit-history',
                       action='store_true',
                       default=None,
                       help='Show audit history for search results.')
    iassc.add_argument('search',
                       default=None,
                       metavar='search_terms',
                       help='Comma separated list of key=value pairs to search ' \
                            'for.\n {0} \n {1}'.format(gen_help('ip_addresses_search'),
                                                       date_help()))
    iassc.set_defaults(func=search_ip_addresses)

    return top_parser, otsp
