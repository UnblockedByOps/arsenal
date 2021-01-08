'''Arsenal client nodes command line parser'''
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
from arsenalclient.cli.node import (
    enc,
    search_nodes,
    create_node,
    delete_nodes,
    )

def parser_nodes(top_parser, otsp):
    '''Add the nodes CLI parser.'''

    ### nodes object_type parser (notp)
    n_help = ('Perform actions on the nodes object_type. Use the search \n'
              'action to perform assignment actions such as tagging, \n'
              'assigning node_groups, and setting status.\n\n')
    notp = otsp.add_parser('nodes',
                           description=n_help,
                           help=n_help,
                           parents=[top_parser])

    # nodes action sub-parser (nasp)
    nasp = notp.add_subparsers(title='Actions',
                               dest='action_command')

    # nodes enc subcommand (nesc)
    nesc = nasp.add_parser('enc',
                           help='Run the puppet ENC.',
                           parents=[top_parser])
    nesc.add_argument('--name',
                      '-n',
                      dest='name',
                      help='The fqdn of the node to search for.',
                      required=True,
                      default=None)
    nesc.add_argument('--inspect',
                      dest='inspect',
                      action='store_true',
                      default=None,
                      help='Print what level of the hierarchy the variable ' \
                      'comes from in brackets after each variable.')
    nesc.set_defaults(func=enc)

    # nodes search subcommand (nssc)
    nssc = nasp.add_parser('search',
                           help='Search for node objects and optionally act upon the results.',
                           parents=[top_parser])
    nssc.add_argument('--fields',
                      '-f',
                      dest='fields',
                      help='Comma separated list of fields to display, or \'all\' for all fields.',
                      default=None)
    nssc.add_argument('--exact',
                      action='store_true',
                      dest='exact_get',
                      default=None,
                      help='Exact match search terms.')
    nssc.add_argument('--exclude',
                      dest='exclude',
                      default=None,
                      help='Comma separated list of key=value pairs to exclude.')
    nssc.add_argument('-a',
                      '--audit-history',
                      action='store_true',
                      default=None,
                      help='Show audit history for search results.')

    # nodes assignment action argument group (ansqg)
    ansag = nssc.add_argument_group('Assignment Actions')

    ansag.add_argument('--status',
                       dest='set_status',
                       help='status to assign to the search results.')
    ansag.add_argument('--tag',
                       dest='set_tags',
                       help='Comma separated list of key=value pairs to tag to the search results.')
    ansag.add_argument('--del_tag',
                       dest='del_tags',
                       help='Comma separated list of key=value pairs to un-tag from ' \
                       'the search results.')
    ansag.add_argument('--node_groups',
                       dest='set_node_groups',
                       help='Comma separated list of node_groups to assign to the search results.')
    ansag.add_argument('--del_node_groups',
                       dest='del_node_groups',
                       help='Comma separated list of node_groups to de-assign from the ' \
                       'search results.')
    ansag.add_argument('--del_all_node_groups',
                       dest='del_all_node_groups',
                       action='store_true',
                       help='De-assign ALL node_groups from the search results.')
    ansag.add_argument('--del_all_tags',
                       dest='del_all_tags',
                       action='store_true',
                       help='De-assign ALL tags from the search results.')
    nssc.add_argument('search',
                      default=None,
                      metavar='search_terms',
                      help='Comma separated list of key=value pairs to search ' \
                      'for.\n {0}'.format(gen_help('nodes_search')))
    nssc.set_defaults(func=search_nodes)

    # nodes create subcommand (ncsc)
    ncsc = nasp.add_parser('create',
                           description='Create node objects.',
                           help='Create node objects.',
                           parents=[top_parser])

    # nodes required argument group (rncag)
    rncag = ncsc.add_argument_group('required arguments')

    ncsc.add_argument('--hardware_profile_id', '-hp',
                      dest='hardware_profile_id',
                      help='hardware_profile_id to assign.',
                      default=1,)
    ncsc.add_argument('--operating_system_id', '-os',
                      dest='operating_system_id',
                      help='operating_system_id to assign.',
                      default=1,)
    rncag.add_argument('--name', '-n',
                       required=True,
                       dest='node_name',
                       help='node_name to create')
    rncag.add_argument('--unique_id', '-u',
                       required=True,
                       dest='unique_id',
                       help='unique_id to assign.')
    rncag.add_argument('--status_id', '-s',
                       required=True,
                       dest='status_id',
                       help='status_id to assign.')
    rncag.set_defaults(func=create_node)

    # nodes delete subcommand (ndsc)
    ndsc = nasp.add_parser('delete',
                           help='Delete node objects. At least one of name, unique_id, ' \
                           'or id is required',
                           parents=[top_parser])
    ndsc.add_argument('--name', '-n',
                      dest='node_name',
                      help='node_name to delete.')
    ndsc.add_argument('--unique_id', '-u',
                      dest='unique_id',
                      help='unique_id to delete.')
    ndsc.add_argument('--id', '-i',
                      dest='node_id',
                      help='node id to delete.')
    ndsc.set_defaults(func=delete_nodes)

    return top_parser, otsp
