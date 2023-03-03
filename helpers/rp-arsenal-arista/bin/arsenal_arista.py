#!/usr/bin/env python3
'''Collect information about Arista TOR switches and register them with Arsenal.'''

import argparse
import configparser
import json
import logging
import sys
import traceback

import pyeapi
import requests

LOG = logging.getLogger(__name__)

# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)


def _parse_args():
    '''Parse all the command line arguments.'''

    my_help="""
    Collect information about Arista TOR switches and register them with Arsenal

    >>> arsenal_arista.py -p SWITCH_NAP9 -l las2
    BEGIN: Registering switches for location: SWITCH_NAP9 - las2
    ...
    """

    pap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                  description=my_help)
    pap.add_argument('-a',
                     '--arsenal-server',
                     help='The Arenal server to use.',
                     default='https://arsenal.las2.fanops.net')
    pap.add_argument('-D',
                     '--dry-run',
                     action='store_true',
                     help='Do not actually change anything. Just print what '
                     'would have happened.')
    pap.add_argument('-d',
                     '--debug',
                     action='store_true',
                     help='Enable debugging.')
    pap.add_argument('-l',
                     '--logical-location',
                     help='The logical location where the switches are located ' \
                     '(ex: las2).',
                     required=True)
    pap.add_argument('-p',
                     '--physical-location',
                     help='The physical location where the switches are located ' \
                     '(ex: SWITCH_NAP9).',
                     required=True)
    pap.add_argument('-S',
                     '--ssl',
                     dest='ssl_verify',
                     help='Whether or not the server is using ssl. Can be ' \
                     'True, False, or path to ca cert',
                     default=True)
    pap.add_argument('-s',
                     '--secrets',
                     dest='secrets_config_file',
                     help='Secret config file to use.',
                     default='/app/rp-arsenal-arista/conf/secrets.ini')

    return pap.parse_args()

def _configure_logging(args):
    '''Set up logging.'''

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    root = logging.getLogger()
    root.setLevel(log_level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    if args.dry_run:
        formatter = logging.Formatter('%(levelname)-8s- DRY RUN: %(message)s')
    else:
        formatter = logging.Formatter('%(levelname)-8s- %(message)s')
    console.setFormatter(formatter)
    root.addHandler(console)

def _parse_config(args):
    '''Parse the config.'''

    secrets_config = configparser.ConfigParser()
    secrets_config.read(args.secrets_config_file)
    setattr(args, 'api_user', secrets_config.get('arista', 'username'))
    setattr(args, 'api_pass', secrets_config.get('arista', 'password'))

    return args

def arsenal_query_api(args, url, http_method, data = None):
    '''Query the Arsenal API.'''

    headers = {
        'Content-Type': 'application/json',
    }

    LOG.debug('Query url: %s', url)
    LOG.debug('http_method is: %s', http_method)
    LOG.debug('data is: %s', json.dumps(data, indent=4, sort_keys=True))

    if http_method == 'get':
        params = {}
        if data:
            params.update(data)

        resp = requests.get(url, headers=headers, verify=args.ssl_verify, params=params)

    if http_method == 'post':
        resp = requests.post(url, headers=headers, verify=args.ssl_verify, json=data)

    if http_method == 'put':
        resp = requests.put(url, headers=headers, verify=args.ssl_verify, json=data)

    resp.raise_for_status()

    try:
        results = resp.json()

        LOG.debug('200 response from url: %s', url)
        LOG.debug(json.dumps(results, sort_keys=True, indent=4))
    except json.decoder.JSONDecodeError:
        results = resp.text
        LOG.warning(results)

    return results

def login(args, username, password):
    '''Guess what this does'''

    payload = {
        'login': username,
        'password': password,
    }

    session = requests.Session()
    session.post(f'{args.arsenal_server}/api/login', data=payload, verify=args.ssl_verify)
    return session

def register(args, session, payload):
    '''Register a node with Arsenal.'''

    headers = {'Content-Type': 'application/json'}
    url = f'{args.server}/api/register'

    resp = session.put(url, headers=headers, json=payload, verify=False)
    if args.debug:
        try:
            LOG.debug(json.dumps(resp.json(), indent=4, sort_keys=True))
        except requests.exceptions.JSONDecodeError:
            LOG.error(resp.text)
    if resp.status_code == 200:
        LOG.info('  Success.')
        return True

    return False

def generate_switch_names(args):
    '''Generate all the assumed switch names based on the rack names
    returned from arsenal.'''

    pl_name = args.physical_location
    ll_name = args.logical_location
    url = f'{args.arsenal_server}/api/physical_racks?physical_location.name=^{pl_name}$'
    all_switches = []

    LOG.info('Retrieiving rack information for physical_location: %s', pl_name)

    resp = arsenal_query_api(args, url, 'get')
    my_racks = resp['results']

    for rack in my_racks:
        sanitized_rack = rack['name'][1:]
        for num in ['1', '2']:
            my_switch = f'msw{sanitized_rack}-{num}.{ll_name}.fanops.net'
            LOG.info('  Adding switch to action list: %s', my_switch)
            all_switches.append(my_switch)

    return all_switches

def process_all_switches(args, all_switches):
    '''Get registration info for all witches and register them with Arsenal.'''

    session = login(args, 'kaboom', 'password')
    failed_switches = []
    total_switch_count = len(all_switches)

    LOG.info('There are %s total switches to register.', total_switch_count)

    current_switch = 0
    for switch_fqdn in all_switches:
        current_switch += 1
        LOG.info('Collecting data for switch: %s (%s of %s)', switch_fqdn,
                                                              current_switch,
                                                              total_switch_count)
        try:
            payload = get_switch_payload(args, switch_fqdn)
        except Exception:
            LOG.error('  Error collecting info from switch! traceback: %s', traceback.format_exc())
            failed_switches.append(switch_fqdn)
            continue

        if args.dry_run:
            LOG.info('  Would have registered switch: %s', switch_fqdn)
        else:
            LOG.info('  Registering switch with Arsenal: %s', switch_fqdn)
            resp = register(args, session, payload)
            if not resp:
                failed_switches.append(switch_fqdn)
    return failed_switches

def get_switch_payload(args, switch_fqdn):
    '''Get all the stuff.'''

    payload = {}
    switch_short_name = switch_fqdn.rsplit('.', 2)[0]

    node = pyeapi.connect(transport='https',
                      host=switch_fqdn,
                      username=args.api_user,
                      password=args.api_pass,
                      return_node=True)

    resp = node.enable('show inventory')
    sys_info = resp[0]['result']['systemInformation']

    payload['name'] = switch_fqdn
    payload['unique_id'] = sys_info['serialNum']
    payload['serial_number'] = sys_info['serialNum']
    payload['hardware_profile'] = {
        'manufacturer': 'Arista Networks',
        'model': sys_info['name'],
        'name': 'Arista Networks ' + sys_info['name'] + ' ' + sys_info['hardwareRev']
    }

    resp = node.enable('show version')
    my_version = resp[0]['result']
    my_name = 'Arista Networks ' + my_version['version']

    payload['operating_system'] = {
        'architecture': my_version['architecture'],
        'description': my_name + ' TOR Swich',
        'name': my_name,
        'variant':  my_version['mfgName'],
        'version_number':  my_version['version'],
    }
    payload['os_memory'] = str(my_version['memTotal'])

    payload['ec2'] = ''
    payload['guest_vms'] = []
    payload['network_interfaces'] = []
    payload['processor_count'] = 1
    payload['uptime'] = str(my_version['uptime'])
    payload['data_center'] = {
        'name': switch_fqdn.split('.')[1]
    }

    LOG.info('  Collecting interface information...')
    interfaces = node.api('interfaces')
    all_interfaces = interfaces.getall()
    for interface in all_interfaces:
        if interface.startswith('Ethernet') and '/' not in interface:
            my_interface = {}
            my_interface['unique_id'] = f'{switch_short_name}-{interface}'
            my_interface['name'] = all_interfaces[interface]['name']
            my_interface['port_switch'] = switch_fqdn
            if all_interfaces[interface]['description']:
                my_interface['port_description'] = all_interfaces[interface]['description']
            resp = node.enable(f"show mac address-table interface {interface}")
            try:
                portinfo = resp[0]['result']['unicastTable']['tableEntries'][0]
                my_interface['port_vlan'] = portinfo['vlanId']
                my_interface['seen_mac_address'] = portinfo['macAddress']
            except (KeyError, IndexError):
                pass

            payload['network_interfaces'].append(my_interface)

    LOG.debug('  payload is:')
    LOG.debug(json.dumps(payload, indent=4, sort_keys=True))

    return payload

def process_failures(failed_switches):
    '''Process the failures and exit accordingly.'''

    returnme = True

    if failed_switches:
        LOG.error('The following switches were unable to be registered: ')
        for switch in failed_switches:
            LOG.error('  %s', switch)
        returnme = False

    return returnme

def main():
    '''Run the main program.'''

    args = _parse_args()
    _configure_logging(args)
    args = _parse_config(args)

    LOG.info('BEGIN: Registering switches for location: %s - %s',
             args.physical_location, args.logical_location)

    all_switches = generate_switch_names(args)
    failed_switches = process_all_switches(args, all_switches)
    exit_ok = process_failures(failed_switches)

    LOG.info('END: Registering switches.')

    if not exit_ok:
        sys.exit(1)

if __name__ == '__main__':
    main()
