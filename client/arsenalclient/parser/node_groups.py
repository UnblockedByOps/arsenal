'''Arsenal client node_groups command line parser'''
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
from argparse import RawTextHelpFormatter
from arsenalclient.cli.common import gen_help
from arsenalclient.cli.common import date_help
from arsenalclient.cli.node_group import (
    search_node_groups,
    create_node_group,
    delete_node_group,
    )

def parser_node_groups(top_parser, otsp):
    '''Add the node_groups CLI parser.'''

    ### node_groups object_type parser (ngotp)
    ng_help = ('Perform actions on the node_groups object_type. Use the \n'
               'search action to perform assignment actions such as tagging.\n\n')
    ngotp = otsp.add_parser('node_groups',
                            description=ng_help,
                            help=ng_help,
                            parents=[top_parser])

    # node_groups action sub-parser (ngasp)
    ngasp = ngotp.add_subparsers(title='Available actions',
                                 dest='action_command')
    # node_groups search subcommand (ngssc)
    ngssc = ngasp.add_parser('search',
                             help='Search for node_group objects and optionally ' \
                             'act upon the results.',
                             parents=[top_parser],
                             formatter_class=RawTextHelpFormatter)
    ngssc.add_argument('--fields',
                       '-f',
                       dest='fields',
                       help='Comma separated list of fields to display, or \'all\' for all fields.',
                       default=None)
    ngssc.add_argument('--exact',
                       action='store_true',
                       dest='exact_get',
                       default=None,
                       help='Exact match search terms.')
    ngssc.add_argument('--exclude',
                       dest='exclude',
                       default=None,
                       help='Comma separated list of key=value pairs to exclude.')
    ngssc.add_argument('-a',
                       '--audit-history',
                       action='store_true',
                       default=None,
                       help='Show audit history for search results.')

    # node_groups update action argument group (anguag)
    anguag = ngssc.add_argument_group('Update Actions')

    anguag.add_argument('--description', '-d',
                        dest='node_group_description',
                        help='Update node_group_description.')
    anguag.add_argument('--owner', '-o',
                        dest='node_group_owner',
                        help='Update node_group_owner.')
    anguag.add_argument('--notes-url', '-u',
                        dest='node_group_notes_url',
                        help='Update node_group_notes_url.')

    # node_groups assignment action argument group (angsag)
    angsag = ngssc.add_argument_group('Assignment Actions')

    angsag.add_argument('--tag',
                        dest='set_tags',
                        help='Comma separated list of key=value pairs to tag to the node_group.')
    angsag.add_argument('--del_tag',
                        dest='del_tags',
                        help='Comma separated list of key=value pairs to un-tag from the ' \
                        'search results.')
    ngssc.add_argument('search',
                       default=None,
                       metavar='search_terms',
                       help='Comma separated list of key=value pairs to search ' \
                            'for:\n{0} \n {1}'.format(gen_help('node_groups_search'),
                                                      date_help()))
    ngssc.set_defaults(func=search_node_groups)

    # node_groups create subcommand (ngcsc)
    ngcsc = ngasp.add_parser('create',
                             help='Create node_group objects.',
                             parents=[top_parser])

    # required node_group create argument group (rngcag)
    rngcag = ngcsc.add_argument_group('required arguments')

    rngcag.add_argument('--name', '-n',
                        required=True,
                        dest='node_group_name',
                        help='node_group_name to create.')
    rngcag.add_argument('--description', '-d',
                        required=True,
                        dest='node_group_description',
                        help='node_group_description to assign.')
    rngcag.add_argument('--owner', '-o',
                        required=True,
                        dest='node_group_owner',
                        help='node_group_owner to assign.')
    rngcag.add_argument('--notes-url', '-u',
                        dest='node_group_notes_url',
                        default=None,
                        help='node_group_notes_url to assign.')
    rngcag.set_defaults(func=create_node_group)

    # node_groups delete subcommand (ngdsc)
    ngdsc = ngasp.add_parser('delete',
                             help='Delete node_group objects.',
                             parents=[top_parser])
    # required node_group delete argument group (rngdag)
    rngdag = ngdsc.add_argument_group('required arguments')

    rngdag.add_argument('--name', '-n',
                        required=True,
                        dest='node_group_name',
                        help='node_group_name to delete.')
    ngdsc.set_defaults(func=delete_node_group)

    return top_parser, otsp
