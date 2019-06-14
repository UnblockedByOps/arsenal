'''Arsenal client UID command line parser'''
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
from arsenalclient.cli.node import unique_id

def parser_uid(top_parser, otsp):
    '''Add the UID parser.  This is a bit of a cheat since technically it's
    not an object type. Print out the unique_id of the current node.'''

    u_help = 'Print out the unique_id of the current node.\n\n'
    uidotp = otsp.add_parser('uid',
                             description=u_help,
                             help=u_help,
                             parents=[top_parser])
    uidotp.set_defaults(func=unique_id)

    return top_parser, otsp
