#!/usr/bin/env python
"""
Register all moonshots that are in DNS with Arsenal.
"""

import sys
import argparse
import configparser
import logging
import json
import socket
import requests
from requests.auth import HTTPBasicAuth
from rp_retry.retry import retry

LOG = logging.getLogger(__name__)
OVERALL_EXIT = 0

# requests is chatty
logging.getLogger('requests').setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()



def _parse_args():
    '''Parse all the command line arguments.'''

    desc = '''
    Register all moonshots that are in DNS with Arsenal.
    Optionally can take a list of moonshot hostnames and only act
    upon those specified.

    >>> arsenal_register_moonshots.py -c moonshots
    INFO    - Finding all moonshots in DNS...
    etc.
    >>> arsenal_register_moonshots.py -c moonshots -n fopp-msf0000-ilo.iad2.fanops.net fopp-msf0001-ilo.iad2.fanops.net
    INFO    - Using chassis list from command line input...
    INFO    -   fopp-msf0000-ilo.iad2.fanops.net
    INFO    -   fopp-msf0001-ilo.iad2.fanops.net
    INFO    - Collecting data from moonshot (1 of 2): fopp-msf0000-ilo.iad2.fanops.net...
    INFO    - Collecting data from moonshot (2 of 2): fopp-msf0001-ilo.iad2.fanops.net...
    INFO    - Registering chassis with Arsenal: fopp-msf0000-ilo.iad2.fanops.net (1 of 2)...
    INFO    - Success.
    INFO    - Registering chassis with Arsenal: fopp-msf0001-ilo.iad2.fanops.net (2 of 2)...
    INFO    - Success.
    INFO    - Successfully registered 2 total chassis.
    '''

    parse = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                    description=desc)
    parse.add_argument('-a',
                       '--arsenal-server',
                       help='The Arsenal server to use.',
                       default='arsenal.las2.fanops.net')
    parse.add_argument('-c',
                       '--chassis-type',
                       help="The chassis type to collect. Valid values are \
                       'moonshots'.",
                       required=True,
                       default='moonshots')
    parse.add_argument('-D',
                       '--dry-run',
                       action='store_true',
                       help='Collect all the info but do not register with '
                       'Arsenal, just print the payload.')
    parse.add_argument('-d',
                       '--debug',
                       action='store_true',
                       help='Enable debugging.')
    parse.add_argument('-n',
                       '--chassis-names',
                       nargs='+',
                       help='A space separated list of chassis to operate on ' \
                       '(optional). If unspecified the script will run on all ' \
                       'chassis in DNS',
                       default=None,)
    parse.add_argument('-s',
                       '--secrets',
                       dest='secrets_config_file',
                       help='Secret config file to use.',
                       default='/app/cluster_automation/conf/secrets.ini')
    parse.add_argument('-S',
                       '--ssl',
                       dest='ssl_verify',
                       help='Whether or not the server is using ssl. Can be True, ' \
                       'False, or path to ca cert',
                       default=False)

    return parse.parse_args()

def configure_logging(args):
    '''Set up logging.'''

    # Set up logging
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

def arsenal_login(server, username, password):
    '''Log into Arsenal. Returns a requests session.'''

    payload = {
        'login': username,
        'password': password,
        'form.submitted': True,
        'api.client': True,
        'return_url': '/api',
    }

    session = requests.Session()
    session.post('{0}/login'.format(server), data=payload, verify=False)
    return session

def get_all_chassis(arsenal_server, chassis_roles):
    '''Build the list of chassis to query from DNS. Returns a list.'''

    LOG.info('Finding all moosnhots in DNS...')
    chassis_list = []
    resp = requests.get('https://{0}/api/data_centers?status=inservice'.format(arsenal_server))
    resp.raise_for_status()

    data_centers = [r['name'] for r in resp.json()['results']]
    LOG.debug(json.dumps(data_centers, sort_keys=True, indent=4))

    for data_center in data_centers:
        for cluster in range(0, 10):
            for chassis_index in range(0, 10):
                for chassis_role in chassis_roles:
                    for env in ['d', 'q', 'p']:
                        try:
                            chassis = f"fop{env}-{chassis_role}{cluster}00{chassis_index}-ilo.{data_center}.fanops.net"
                            resp = socket.gethostbyname(chassis)
                            LOG.info('chassis found: %s', chassis)
                            chassis_list.append(chassis)
                        except socket.gaierror:
                            LOG.debug('Moonshot not found: %s', chassis)

    LOG.debug(json.dumps(chassis_list, sort_keys=True, indent=4))
    LOG.info('Found %s moonshots in DNS.', len(chassis_list))

    chassis_list = filter_chassis(arsenal_server, chassis_list)
    LOG.info('Found %s moonshots  matched state requirement in arsenal.', len(chassis_list))

    return chassis_list

def filter_chassis(arsenal_server, chassis_list):
    ''' filter out chassis that not in arsenal or marked as maintenance '''

    filter_chassis_list = []

    endpoint = 'https://{0}/api/nodes'.format(arsenal_server)

    hostname_pattern = "|".join(chassis_list)

    payload = {
        'name': hostname_pattern,
        'status': "maintenance,broken",
    }

    resp = requests.get(endpoint, params=payload)
    resp.raise_for_status()
    my_json = resp.json()

    LOG.debug('Results are: %s', json.dumps(my_json, sort_keys=True, indent=4))

    results = my_json['results']

    oos_chassis_list = []

    for chassis in results:
        oos_chassis_list.append(chassis["name"])

    return [item for item in chassis_list if item not in oos_chassis_list]

@retry(5, requests.exceptions.HTTPError, requests.exceptions.ConnectionError, time_delay=5)
def query_moonshot(args, ms_fqdn, endpoint):
    '''Make http requests to the moonshot.'''

    headers = {'Content-Type': 'application/json'}
    auth = HTTPBasicAuth(args.chassis_user, args.chassis_pass)

    url = 'https://{0}{1}'.format(ms_fqdn, endpoint)
    LOG.debug('Query uri: {0}'.format(url))

    try:

        LOG.debug('Submitting get to url: {0}'.format(url))
        resp = requests.get(url, headers=headers, auth=auth, verify=False)

        resp.raise_for_status()
        if resp.status_code == 200:

            results = resp.json()

            LOG.debug('200 response from url: {0}'.format(url))
            LOG.debug(results)

            return results

    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        raise

    except Exception as ex:
        LOG.error('moonshot API query failed: {0}'.format(ex))
        raise

def collect_moonshots(args, moonshots):
    '''Collect all the info on all the moonshots. Returns a list of payloads to
    'register with Arsenal.'''

    global OVERALL_EXIT
    all_moonshots = []
    failed_chassis = []

    total = len(moonshots)
    current = 1
    for moonshot in moonshots:
        LOG.info('Collecting data from moonshot ({0} of {1}): {2}...'.format(current,
                                                                             total,
                                                                             moonshot))
        current += 1
        payload = {
            'name': moonshot,
            'status_id': 2,
            'hardware_profile': {
                'model': '',
                'manufacturer': 'HP',
                'name': '',
                'id': None
            },
            'operating_system': {
                'version_number': '',
                'description': 'HP CM Firmware',
                'variant': 'HP',
                'architecture': 'x86_64',
                'id': None,
                'name': ''
            },
            'network_interfaces': [],
            'ec2': None,
            'guest_vms': [],
            'uptime': '',
            'processor_count': 1,
        }
        try:
            resp = query_moonshot(args, moonshot, '/rest/v1/Chassis/1')
        except Exception:
            LOG.error('Unable to contact moonshot: {0}'.format(moonshot))
            failed_chassis.append(moonshot)
            OVERALL_EXIT = 1
            continue

        LOG.debug(json.dumps(resp, indent=2, sort_keys=True))

        firmware = resp['Oem']['Hp']['Firmware']['ChassisManagementFirmware']['Current']['VersionString']
        chassis_network = resp['Oem']['Hp']['ChassisManager'][0]

        network = {
            'name': 'eth0',
            'unique_id': chassis_network['MAC'],
            'ip_address': chassis_network['IP'],
        }

        payload['network_interfaces'].append(network)

        payload['serial_number'] = resp['SerialNumber']
        payload['unique_id'] = resp['Oem']['Hp']['Location']['LocationOfChassis']['UUID']
        payload['hardware_profile']['model'] = resp['Model'][3:]
        payload['hardware_profile']['name'] = resp['Model']
        payload['operating_system']['version_number'] = firmware
        payload['operating_system']['name'] = 'HP CM Firmware {0} x86_64'.format(firmware)

        LOG.debug(json.dumps(payload, indent=4, sort_keys=True))
        all_moonshots.append(payload)

    return all_moonshots, failed_chassis

def register(args, all_chassis):
    '''Register all the chasssis with Arsenal.'''

    headers = {'Content-Type': 'application/json'}
    server = f'https://{args.arsenal_server}'
    url = f'{server}/api/register'
    session = arsenal_login(server, 'kaboom', 'password')

    global OVERALL_EXIT

    total = len(all_chassis)
    complete = 1
    success = 0

    for chassis in all_chassis:
        name = chassis['name']

        LOG.info("Registering chassis with Arsenal: %s (%s of %s)...", name,
                                                                       complete,
                                                                       total,)
        complete += 1
        if args.dry_run:
            LOG.info('Skipping registration, here is the payload we would have sent:')
            LOG.info(json.dumps(chassis, sort_keys=True, indent=4))
            success += 1
            continue

        resp = session.put(url, headers=headers, json=chassis, verify=False)

        if resp.status_code == 200:
            LOG.info('Success.')
            success += 1
            assign_node_group(args, resp)
        else:
            OVERALL_EXIT = 1
            LOG.error('There was a problem registering chassis: %s', name)
            LOG.error(resp.text)

    return success

def assign_node_group(args, resp):
    """
    Assign node group to node if possible.
    """

    results = resp.json()
    result = results['results'][0]
    node_name = result['name']
    node_id = result['id']
    node_group = f"{node_name[0:3]}_{node_name[5:8]}"
    global OVERALL_EXIT

    LOG.info("Attempting to assign node_group: %s to server: %s", node_group, node_name)

    headers = {'Content-Type': 'application/json'}
    server = f'https://{args.arsenal_server}'
    session = arsenal_login(server, args.enc_user, args.enc_pass)

    url = f'{server}/api/node_groups'
    params = {
        "name": f"^{node_group}$"
    }
    try:
        resp = session.get(url, headers=headers, params=params)
        results = resp.json()
        result = results['results'][0]
        node_group_id = result['id']
    except IndexError:
        OVERALL_EXIT = 1
        LOG.error("node_group: %s not found in Arsenal.", node_group)
        return
    except Exception as ex:
        OVERALL_EXIT = 1
        LOG.error("There was an error finding the node_group: %s in arsenal: %s", node_group, ex)
        return

    try:
        data = {
            "nodes": [
                node_id,
            ]
        }
        url = f"{server}/api/node_groups/{node_group_id}/nodes"
        resp = session.put(url, headers=headers, json=data, verify=False)
        resp.raise_for_status()
        LOG.info("Success.")
    except Exception as ex:
        OVERALL_EXIT = 1
        LOG.error("There was an error assigning the node_group to the node: %s", ex)

def main():
    '''Do Stuff.'''

    args = _parse_args()
    configure_logging(args)

    secrets_config = configparser.ConfigParser()
    secrets_config.read(args.secrets_config_file)
    setattr(args, 'chassis_user', secrets_config.get('moonshot', 'username'))
    setattr(args, 'chassis_pass', secrets_config.get('moonshot', 'password'))
    setattr(args, 'enc_user', secrets_config.get('external-enc', 'username'))
    setattr(args, 'enc_pass', secrets_config.get('external-enc', 'password'))

    chassis_roles = {
        'moonshots': [
            'msf',
            'msx',
            'mss',
            'mns'
        ]
    }

    if args.chassis_names:
        LOG.info('Using chassis list from command line input...')
        for chassis in args.chassis_names:
            LOG.info('  %s', chassis)
        chassis_list = args.chassis_names
    else:
        chassis_list = get_all_chassis(args.arsenal_server,
                                       chassis_roles['moonshots'])

    all_chassis, failed_dns_chassis = collect_moonshots(args, chassis_list)

    success_count = register(args, all_chassis)
    LOG.info('Successfully registered %s total chassis.', success_count)

    if failed_dns_chassis:
        LOG.error('The following chassis were found in DNS but unable to be reached:')
        for failed in failed_dns_chassis:
            LOG.error('  %s', failed)

    sys.exit(OVERALL_EXIT)

if __name__ == '__main__':
    main()
