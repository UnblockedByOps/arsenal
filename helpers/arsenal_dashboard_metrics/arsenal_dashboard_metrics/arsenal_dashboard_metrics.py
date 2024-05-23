#!/usr/bin/env python
"""
Collect metrics from Arsenal status endpoints and send
them to graphite.
"""

import argparse
import socket
import time
import requests


def _parse_args():
    '''Parse all the command line arguments.'''

    desc = '''
    Gather monitoring dashboard metrics and send them to graphite.

    >>> collect_dashboard_metrics.py -H graphite.mydomain.com -P 3003 -s ~/conf/collect_dashboard_metrics.ini
    Colleting...
    '''

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=desc)
    parser.add_argument('-a',
                        '--arsenal',
                        dest='arsenal_server',
                        help='Host name of the arsenal server.',
                        default='arsenal.las2.fanops.net')
    parser.add_argument('-H',
                        '--host',
                        dest='host_fqdn',
                        help='Host name of the graphite server.',
                        default='graphite')
    parser.add_argument('-P',
                        '--port',
                        dest='host_port',
                        help='Port number of the graphite server.',
                        default='3003')
    parser.add_argument('-S',
                        '--ssl',
                        dest='ssl_verify',
                        help='Whether or not the server is using ssl. ' \
                        'Can be True, False, or path to ca cert',
                        default=None)
    parser.add_argument('-D',
                        '--dry-run',
                        action='store_true',
                        help='Do not send metrics to graphite, just print them.')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Enable debugging.')
    parser.add_argument('-s',
                        '--success-file',
                        help='The file to write to upon sucessfully completeing.',
                        default='/app/mgni-arsenal_dashboard_metrics/success.txt')

    return parser.parse_args()

def get_data(server, uri, params=None, data_type=None):
    '''Get data from arsenal API.'''

    headers = {'Content-Type': 'application/json', }

    url = f"https://{server}/{uri}"

    resp = requests.get(url, headers=headers, params=params)
    results = resp.json()

    if data_type == 'total':
        return int(results['meta']['total'])

    return results

def get_path(input_dict):
    """
    Traverse a dictionary to get the full metric path.
    """

    for key, value in input_dict.items():
        if isinstance(value, dict):
            for sub_key in get_path(value):
                yield key + '.' + sub_key
        else:
            yield key

def prep_node_metrics(args, results):
    '''Prep node-based metrics and send them graphite.'''

    now = int(time.time())

    for data_center, values in results['results'][0].items():
        for path in get_path(values):
            metric_name = f"dashboards.arsenal.nodes.dc.{data_center}.{path}"
            split_path = path.split('.')
            my_value = values.get(split_path[0])
            for remainder in split_path[1:]:
                my_value = my_value.get(remainder)
            metric = f"{metric_name} {my_value} {now}"
            send_metric(args, metric)

def prep_stale_node_metrics(args, results):
    '''Prep stale node metric and send them to graphite.'''

    now = int(time.time())

    metric = 'dashboards.arsenal.nodes.stale_last_registered.inservice_count ' \
             '{0} {1}'.format(results['meta']['total'], now)
    send_metric(args, metric)

def prep_db_metrics(args, results):
    '''Prep db-based metrics and send them to graphite.'''

    now = int(time.time())

    for key, val in results['results'][0]['row_counts'].items():
        metric = 'dashboards.arsenal.db.row_counts.{0}_count ' \
                 '{1} {2}'.format(key, val, now)
        send_metric(args, metric)

def send_metric(args, message):
    '''Send metric to graphite.'''

    server_ip = socket.gethostbyname(args.host_fqdn)
    server_port = int(args.host_port)

    if args.dry_run:

        print(f'sending metric - server: {args.host_fqdn} port: {args.host_port} message: {message}')

    else:

        try:
            sock = socket.socket()
            sock.connect((server_ip, server_port))
            sock.sendall(f'{message}\n'.encode())
            sock.close()
            print('metric sent')
        except:
            print('failed to send')
            raise

def write_success(args):
    """
    Write a timestamp to a file upon successsfully completing.
    """

    now = time.time()
    with open(args.success_file, "w", encoding="utf-8") as my_file:
        my_file.write(f"Last success time: {now}\n")

def main():
    '''Do all the things'''

    # parse the args
    args = _parse_args()

    results = get_data(args.arsenal_server, '/api/reports/nodes')
    prep_node_metrics(args, results)

    results = get_data(args.arsenal_server, '/api/reports/db')
    prep_db_metrics(args, results)

    results = get_data(args.arsenal_server, '/api/reports/stale_nodes')
    prep_stale_node_metrics(args, results)

    write_success(args)

if __name__ == '__main__':
    main()
