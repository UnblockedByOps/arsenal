'''Arsenal client tags command line parser'''
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
from arsenalclient.cli.tag import (
    search_tags,
    create_tag,
    delete_tag,
    )

def parser_tags(top_parser, otsp):
    '''Add the tags CLI parser.'''

    ### tags object_type parser (totp)
    t_help = ('Perform actions on the tags object_type. Use the search\n'
              'action to perform assignment actions such as tagging.\n\n')
    totp = otsp.add_parser('tags',
                           description=t_help,
                           help=t_help,
                           parents=[top_parser])

    # tags action sub-parser (tasp)
    tasp = totp.add_subparsers(title='Available actions',
                               dest='action_command')
    # tags search subcommand (tssc)
    tssc = tasp.add_parser('search',
                           help='Search for tags objects and optionally act upon the results.',
                           parents=[top_parser],
                           formatter_class=RawTextHelpFormatter)
    tssc.add_argument('--fields',
                      '-f',
                      dest='fields',
                      help='Comma separated list of fields to display, or \'all\' for all fields.',
                      default=None)
    tssc.add_argument('--exact',
                      action='store_true',
                      dest='exact_get',
                      default=None,
                      help='Exact match search terms.')
    tssc.add_argument('--exclude',
                      dest='exclude',
                      default=None,
                      help='Comma separated list of key=value pairs to exclude.')
    tssc.add_argument('-a',
                      '--audit-history',
                      action='store_true',
                      default=None,
                      help='Show audit history for search results.')

    # tags assignment action argument group (atsag)
    atsag = tssc.add_argument_group('Assignment Actions')

    atsag.add_argument('--tag',
                       dest='set_tags',
                       help='Comma separated list of key=value pairs to tag to the node_group.')
    tssc.add_argument('search',
                      default=None,
                      metavar='search_terms',
                      help='Comma separated list of key=value pairs to search ' \
                           'for:\n{0} \n {1}'.format(gen_help('tags_search'),
                                                     date_help()))
    atsag.set_defaults(func=search_tags)

    # tags create subcommand (tcsc)
    tcsc = tasp.add_parser('create',
                           help='Create tag objects.',
                           parents=[top_parser])

    # required tag create argument group (rtcag)
    rtcag = tcsc.add_argument_group('required arguments')

    rtcag.add_argument('--name', '-n',
                       required=True,
                       dest='tag_name',
                       help='tag_name to create.')
    rtcag.add_argument('--value',
                       required=True,
                       dest='tag_value',
                       help='tag_value to assign to the name.')
    rtcag.set_defaults(func=create_tag)

    # tags delete subcommand (tdsc)
    tdsc = tasp.add_parser('delete',
                           help='Delete tag objects.',
                           parents=[top_parser])

    # required tag delete argument group (rtdag)
    rtdag = tdsc.add_argument_group('required arguments')

    rtdag.add_argument('--name', '-n',
                       required=True,
                       dest='tag_name',
                       help='tag_name to delete.')
    rtdag.add_argument('--value',
                       required=True,
                       dest='tag_value',
                       help='tag_value to delete.')
    tdsc.set_defaults(func=delete_tag)

    return top_parser, otsp
