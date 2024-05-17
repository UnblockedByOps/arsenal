#!/usr/bin/env python3
'''Collect information about Arista TOR switches and register them with Arsenal.'''

import argparse
import configparser
import json
import logging
import sys
import socket
import traceback
import yaml

import pyeapi
import requests

LOG = logging.getLogger(__name__)

# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pyeapi.eapilib").setLevel(logging.CRITICAL)


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
    pap.add_argument('-y',
                     '--yaml-config',
                     help='Yaml config file.',
                     default='/app/rp-arsenal-arista/conf/config.yaml')

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

def load_yaml(yaml_file):
    '''Load in the data from yaml_file and return a YAML() object.'''

    LOG.info('Loading data from yaml file: %s', yaml_file)

    with open(yaml_file, 'r', encoding='utf-8') as config_fd:
        my_yaml = yaml.safe_load(config_fd)

    return my_yaml

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
    url = f'{args.arsenal_server}/api/register'

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

def get_switch_ips(args):
    '''Return a list of ips of all the switches found in Arsenal as physical devices if they
    have an oob_ip_address defined and have any status other than broken,
    maintenance, or decom.'''

    pl_name = args.physical_location
    url = f"{args.arsenal_server}/api/physical_devices"
    data = {
        "physical_location.name": f"^{pl_name}$",
        "hardware_profile.name": "Arista",
        "ex_status": "broken,maintenance,decom",
        "fields": "oob_ip_address",
    }
    all_switches = []

    LOG.info('Retrieving rack information for physical_location: %s', pl_name)

    resp = arsenal_query_api(args, url, 'get', data=data)
    my_results = resp['results']

    for result in my_results:
        if result['oob_ip_address']:
            LOG.info('  Adding switch to action list: %s', result['oob_ip_address'])
            all_switches.append(result['oob_ip_address'])
        else:
            LOG.warning('  No oob_ip_address for switch: %s', result['serial_number'])

    return all_switches

def process_all_switches(args, exclude_switches, all_switches):
    '''Get registration info for all witches and register them with Arsenal.'''

    session = login(args, 'kaboom', 'password')
    success_switches = []
    failed_switches = []
    total_switch_count = len(all_switches)

    LOG.info('There are %s total switches to register.', total_switch_count)

    current_switch = 0
    for switch_ip in all_switches:
        current_switch += 1
        if switch_ip in exclude_switches:
            LOG.warning('Switch is in exclude config: %s skipping (%s of %s).', switch_ip,
                                                                                current_switch,
                                                                                total_switch_count)
            continue
        LOG.info('Collecting data for switch: %s (%s of %s)...', switch_ip,
                                                                 current_switch,
                                                                 total_switch_count)
        try:
            payload = get_switch_payload(args, switch_ip)
        except KeyError as ex:
            LOG.error('  KeyError collecting info from switch: %s', ex)
            LOG.debug('  traceback: %s', traceback.format_exc())
            fail = {
                'name': switch_ip,
                'error': f'KeyError: {ex}',
            }
            failed_switches.append(fail)
            continue
        except (pyeapi.eapilib.ConnectionError, ConnectionRefusedError) as ex:
            LOG.error('  Connection refused collecting info from switch: %s', ex)
            LOG.debug('  traceback: %s', traceback.format_exc())
            fail = {
                'name': switch_ip,
                'error': f'Connection error: {ex}',
            }
            failed_switches.append(fail)
            continue
        except Exception as ex:
            LOG.error('  Unknown Errror collecting info from switch: %s', ex)
            LOG.debug('  traceback: %s', traceback.format_exc())
            fail = {
                'name': switch_ip,
                'error': 'Unknown, see console output for more info.'
            }
            failed_switches.append(fail)
            continue

        if args.dry_run:
            LOG.info('  Would have registered switch: %s', switch_ip)
            success = {
                'name': switch_ip,
                'serial_number': payload['serial_number'],
            }
            success_switches.append(success)
        else:
            LOG.info('  Registering switch with Arsenal: %s', switch_ip)
            resp = register(args, session, payload)
            if not resp:
                failed_switches.append(switch_ip)
                fail = {
                    'name': switch_ip,
                    'error': 'Failed to register with Arsenal.'
                }
                failed_switches.append(fail)
            success = {
                'name': switch_ip,
                'serial_number': payload['serial_number'],
            }
            success_switches.append(success)

    return success_switches, failed_switches

def get_switch_payload(args, switch_ip):
    '''Get all the stuff.'''

    payload = {}

    node = pyeapi.connect(transport='https',
                      host=switch_ip,
                      username=args.api_user,
                      password=args.api_pass,
                      return_node=True)

    resp = node.enable('show hostname')
    switch_short_name = resp[0]['result']['hostname']
    switch_fqdn = f"{switch_short_name}.fanops.net"
    LOG.info('  Switch fqdn is: %s', switch_fqdn)

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
    try:
        my_variant = my_version['mfgName']
    except KeyError:
        my_variant = 'Arista'

    payload['operating_system'] = {
        'architecture': my_version['architecture'],
        'description': my_name + ' TOR Swich',
        'name': my_name,
        'variant':  my_variant,
        'version_number':  my_version['version'],
    }
    payload['os_memory'] = str(my_version['memTotal'])

    try:
        my_uptime = str(my_version['uptime'])
    except KeyError:
        my_uptime = '1'

    payload['ec2'] = ''
    payload['guest_vms'] = []
    payload['network_interfaces'] = []
    payload['processor_count'] = 1
    payload['uptime'] = my_uptime
    payload['data_center'] = {
        'name': switch_fqdn.split('.')[1]
    }

    LOG.info('  Collecting interface information...')
    interfaces = node.api('interfaces')
    all_interfaces = interfaces.getall()
    for interface in all_interfaces:
        if interface.startswith('Ethernet'):
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

def process_success(success_switches):
    '''Process the successes.'''

    LOG.info('The following switches were successfully registered with Arsenal: ')

    for switch in success_switches:
        LOG.info('  switch: %s serial_number: %s', switch['name'], switch['serial_number'])

def process_failures(failed_switches):
    '''Process the failures and exit accordingly.'''

    returnme = True

    if failed_switches:
        LOG.error('The following switches were unable to be registered: ')
        for switch in failed_switches:
            LOG.error('  switch: %s error: %s', switch['name'], switch['error'])
        returnme = False

    return returnme

def main():
    '''Run the main program.'''

    args = _parse_args()
    _configure_logging(args)
    args = _parse_config(args)

    LOG.info('BEGIN: Registering switches for location: %s - %s',
             args.physical_location, args.logical_location)

    all_switches = [
        'superspine-1.las2.fanops.net',
        'mleaf-1.las2.fanops.net',
        'core3.las2.fanops.net',
        'border3.iad2.fanops.net',
    ]

#    all_switches = get_switch_ips(args)
    yaml_config = load_yaml(args.yaml_config)
    success_switches, failed_switches = process_all_switches(args,
                                                             yaml_config['exclude_switches'],
                                                             all_switches)
    process_success(success_switches)
    exit_ok = process_failures(failed_switches)

    msg = 'END: Registering switches.'

    if not exit_ok:
        LOG.error(msg)
        sys.exit(1)

    LOG.info(msg)

if __name__ == '__main__':
    main()
