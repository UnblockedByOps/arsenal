'''Arsenal client physical_elevations command line parser'''
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
from arsenalclient.cli.physical_elevation import (
    search_physical_elevations,
    create_physical_elevation,
    delete_physical_elevation,
    )

def parser_physical_elevations(top_parser, otsp):
    '''Add the physical_elevations CLI parser.'''

    ### physical_elevations object_type parser (otp)
    my_help = 'Perform actions on the physical_elevations object_type.\n\n'
    otp = otsp.add_parser('physical_elevations',
                          description=my_help,
                          help=my_help,
                          parents=[top_parser])

    # physical_elevations action sub-parser (asp)
    asp = otp.add_subparsers(title='Available actions',
                             dest='action_command')
    # physical_elevations search subcommand (ssc)
    ssc = asp.add_parser('search',
                         help='Search for physical_elevation objects and optionally ' \
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

    # physical_elevations update action argument group (uaag)
    uaag = ssc.add_argument_group('Update Actions')

    uaag.add_argument('-l',
                      '--location',
                      dest='physical_location',
                      help='Update physical_elevation location. Must also ' \
                      'specify rack.')
    uaag.add_argument('-r',
                      '--rack',
                      dest='physical_rack',
                      help='Update physical_elevation location. Must also ' \
                      'specify location.')

    ssc.add_argument('search',
                     default=None,
                     metavar='search_terms',
                     help='Comma separated list of key=value pairs to search ' \
                          'for.\n {0} \n {1}'.format(gen_help('physical_elevations_search'),
                                                     date_help()))
    ssc.set_defaults(func=search_physical_elevations)

    # physical_elevations create subcommand (csc)
    csc = asp.add_parser('create',
                         help='Create physical_elevation objects.',
                         parents=[top_parser])

    # required physical_elevation create argument group (rcag)
    rcag = csc.add_argument_group('required arguments')

    rcag.add_argument('-e',
                      '--elevation',
                      dest='physical_elevation',
                      required=True,
                      help='The physical rack elevation name.')
    rcag.add_argument('-l',
                      '--location',
                      dest='physical_location',
                      required=True,
                      help='The physical rack location name.')
    rcag.add_argument('-r',
                      '--rack',
                      dest='physical_rack',
                      required=True,
                      help='The physical rack name.')

    rcag.set_defaults(func=create_physical_elevation)

    # physical_elevations delete subcommand (dsc)
    dsc = asp.add_parser('delete',
                         help='Delete physical_elevation objects.',
                         parents=[top_parser])

    # required physical_elevation delete argument group (rdag)
    rdag = dsc.add_argument_group('required arguments')

    rdag.add_argument('-e',
                      '--elevation',
                      dest='physical_elevation',
                      required=True,
                      help='The physical rack elevation name to delete.')
    rdag.add_argument('-l',
                      '--location',
                      dest='physical_location',
                      required=True,
                      help='The physical rack location name to delete.')
    rdag.add_argument('-r',
                      '--rack',
                      dest='physical_rack',
                      required=True,
                      help='The physical rack name to delete.')
    dsc.set_defaults(func=delete_physical_elevation)

    return top_parser, otsp
