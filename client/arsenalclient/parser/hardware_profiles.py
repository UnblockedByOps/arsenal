'''Arsenal client hardware_profiles command line parser'''
#
#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the 'License");
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
from arsenalclient.cli.hardware_profile import (
    search_hardware_profiles,
    )

def parser_hardware_profiles(top_parser, otsp):
    '''Add the hardware_profiles CLI parser.'''

    ### hardware_profiles object_type parser (sotp)
    s_help = ('Perform actions on the hardware_profiles object_type. Use the \n'
              'search action to perform actions such as updating '
              'the rack_u or rack_color.\n\n')
    sotp = otsp.add_parser('hardware_profiles',
                           description=s_help,
                           help=s_help,
                           parents=[top_parser])

    # hardware_profiles action sub-parser (sasp)
    # https://bugs.python.org/issue16308
    if sys.version_info.major == 2 or sys.version_info.minor < 7:
        sasp = sotp.add_subparsers(title='Available actions',
                                   dest='action_command')
    else:
        sasp = sotp.add_subparsers(title='Available actions',
                                   dest='action_command',
                                   required=True)

    # hardware_profiles search subcommand (sssc)
    sssc = sasp.add_parser('search',
                           help='Search for hardware_profile objects and optionally act upon the results.',
                           parents=[top_parser],
                           formatter_class=RawTextHelpFormatter)
    sssc.add_argument('--fields',
                      '-f',
                      dest='fields',
                      help='Comma separated list of fields to display, or \'all\' for all fields.',
                      default=None)
    sssc.add_argument('--exact',
                      action='store_true',
                      dest='exact_get',
                      default=None,
                      help='Exact match search terms.')
    sssc.add_argument('--exclude',
                      dest='exclude',
                      default=None,
                      help='Comma separated list of key=value pairs to exclude.')
    sssc.add_argument('-a',
                      '--audit-history',
                      action='store_true',
                      default=None,
                      help='Show audit history for search results.')

    # hardware_profiles update action argument group (anguag)
    suag = sssc.add_argument_group('Update Actions')
    suag.add_argument('--rack-color', '-c',
                      dest='hardware_profiles_rack_color',
                      help='Update the html color of a hardware_profile ' \
                      'for display in the UI.')
    suag.add_argument('--rack-u', '-u',
                      dest='hardware_profiles_rack_u',
                      help='Update the number of rack u a hardware_profile ' \
                      'occupies.')
    sssc.add_argument('search',
                      default=None,
                      metavar='search_terms',
                      help='Comma separated list of key=value pairs to search ' \
                      'for:\n{0} \n {1}'.format(gen_help('hardware_profiles_search'), date_help()))
    sssc.set_defaults(func=search_hardware_profiles)

    return top_parser, otsp
