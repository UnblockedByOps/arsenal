#!/usr/local/bin/python2.7
'''Search arsenal and generate ansible inventory.'''
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
import sys
import argparse
import requests

# Requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()

LOG = logging.getLogger(__name__)

def parse_args():
    '''Parse all the command line arguments.'''

    help_desc = '''
    Search arsenal and generate ansible inventory.
    >>> arsenal_ansible_inventory.py -m datacenter -n fopp-pup
    INFO    - BEGIN: Generating ansible inventory.
    INFO    - END: Generating ansible inventory.
    >>> arsenal_ansible_inventory.py -m role -n fopp-(cbl|pup)
    INFO    - BEGIN: Generating ansible inventory.
    INFO    - END: Generating ansible inventory.
    '''

    pap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                  description=help_desc)
    pap.add_argument('-a',
                     '--arsenal_server',
                     help='FQDN of the arsenal server to use.',
                     default='arsenal')
    pap.add_argument('-d',
                     '--debug',
                     action='store_true',
                     help='Enable debugging.')
    pap.add_argument('-e',
                     '--exclude',
                     help='nodes to exclude from the search.',
                     default=None)
    pap.add_argument('-i',
                     '--inventory_file',
                     help='Full path and name of the inventory file to write. '
                     'default: ./ansible_inventory.ini',
                     default='ansible_inventory.ini')
    pap.add_argument('-m',
                     '--mode',
                     help='Mode to sort results by. Choices are "datacenter" '
                     'or "role".',
                     default=None)
    pap.add_argument('-n',
                     '--nodes',
                     help='nodes to search for.',
                     default=None)
    pap.add_argument('-s',
                     '--status',
                     help='Status to search for. default: inservice',
                     default='inservice')
    pap.add_argument('-S',
                     '--ssl',
                     dest='ssl_verify',
                     help='Whether or not the server is using ssl. Can be True, False, ' \
                     'or path to ca cert',
                     default=False)

    return pap.parse_args()

def get_sort_order(node):
    '''Return Return a tuple for sorting via datacenter first, then node.'''

    return node.split('.')[1], node.split('.')[0]

def configure_logging(args):
    '''Set up logging.'''

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    root = logging.getLogger()
    root.setLevel(log_level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    formatter = logging.Formatter('%(levelname)-8s- %(message)s')
    console.setFormatter(formatter)
    root.addHandler(console)

def check_req_params(args):
    '''Make sure we have required args.'''

    required = [
        'mode',
        'nodes',
    ]

    for req in required:
        if not args.__dict__[req]:
            LOG.error('Required option is missing: {0}\n'.format(req))
            sys.exit(2)

def query_arsenal(args):
    '''Query Arsenal for servers. Returns a dict.'''

    url = 'https://{0}/api/nodes?name={1}&status={2}'.format(args.arsenal_server,
                                                             args.nodes,
                                                             args.status)
    if args.exclude:
        url += '&ex_name={0}'.format(args.exclude)

    if args.debug:
        LOG.debug('Arsenal url: {0}'.format(url))

    results = {}
    try:
        headers = {'Content-Type': 'application/json'}
        resp = requests.get(url, headers=headers, verify=args.ssl_verify)
        node_list = resp.json()
    except Exception as ex:
        LOG.error('There was an issue querying arsenal: {0}, '
                  'aborting!'.format(ex))
        sys.exit(1)

    if len(node_list['results']) == 0:
        LOG.error('No results found in arsenal, aborting!')
        sys.exit(1)

    for node in node_list['results']:
        if args.mode == 'datacenter':
            key = node['name'].split('.')[1]
        elif args.mode == 'role':
            key = node['name'][5:8]
        else:
            LOG.error('Invalid mode specified: {0}'.format(args.mode))
            sys.exit(1)
        results.setdefault(key, []).append(node['name'])

    return results

def write_inventory(args, results):
    '''Write out the results to the inventory file.'''

    with open(args.inventory_file, 'w') as the_file:
        for result in results:
            the_file.write('[{0}]\n'.format(result))

            if args.mode == 'datacenter':
                for node in sorted(results[result]):
                    the_file.write('{0}\n'.format(node))
            elif args.mode == 'role':
                for node in sorted(results[result], key=get_sort_order):
                    the_file.write('{0}\n'.format(node))

def main():
    '''Do Stuff.'''

    args = parse_args()
    configure_logging(args)
    check_req_params(args)

    LOG.info('BEGIN: Generating ansible inventory.')

    results = query_arsenal(args)
    write_inventory(args, results)

    LOG.info('END: Generating ansible inventory.')

if __name__ == '__main__':
    main()
