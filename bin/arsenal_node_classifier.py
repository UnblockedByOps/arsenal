#!/usr/bin/python
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
import logging
import argparse
import yaml
import arsenalclientlib as client

log = logging.getLogger(__name__)


class Args:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def main():

    # FIXME: Fix the client so this stuff isn't required
    a = {
         'verbose': False,
         'quiet': True,
         'write_log': False,
         'log_file': '',
         'user_login': 'test',
    }
    args = Args(**a)

    parser = argparse.ArgumentParser(description='Arsneal node classifier for use with puppet.')
    parser.add_argument('node_name',
                        help='an integer for the accumulator')

    node_args = parser.parse_args()

    client.main('/app/arsenal/conf/arsenal.ini', args = args)

    log.info('Searching for node: node_name={0}'.format(node_args.node_name))

    output = {}
    output['classes'] = []

    results = client.object_search('nodes', 'node_name={0}'.format(node_args.node_name), True)

    if results:
        for ng in results[0]['node_groups']:
            output['classes'].append(ng['node_group_name'])

    print(yaml.safe_dump(output, default_flow_style=False, explicit_start=True))

if __name__ == '__main__':
    main()

