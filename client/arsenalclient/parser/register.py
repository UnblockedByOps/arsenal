'''Arsenal client register command line parser'''
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
from arsenalclient.cli.node import register

def parser_register(top_parser, otsp):
    '''Add the register CLI parser.  This is a bit of a cheat since technically
    it's not an object type. Putting it at the top level since it is the
    primary command.'''

    r_help = 'Register this node to the server.\n\n'
    rotp = otsp.add_parser('register',
                           description=r_help,
                           help=r_help,
                           parents=[top_parser])
    rotp.set_defaults(func=register)

    return top_parser, otsp
