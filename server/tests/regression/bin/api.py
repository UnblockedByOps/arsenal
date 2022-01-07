#!/usr/bin/python
'''
Test arsenal api endpoints to ensure they return correctly.
'''
import sys
import configparser
import logging
import argparse
import json
from ruamel.yaml import YAML
import requests
from rp_retry.retry import retry
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import NewConnectionError
from test_register import REGISTER_TEST_CASES

LOG = logging.getLogger(__name__)
# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()

OVERALL_FAIL = 0
FAILED_TESTS = []

def ar_login(server, username, password):
    '''Create a session and log into arsenal. Returns a requests session object.'''

    session = requests.Session()

    payload = {
        'form.submitted': True,
        'api.client': True,
        'return_url': '/api',
        'login': username,
        'password': password,
    }
    url = '{0}/login'.format(server)
    resp = session.post(url,
                        data=payload,
                        verify=False)

    LOG.debug('login cookies: {0}'.format(session.cookies.get_dict()))
    LOG.debug('login response: {0}'.format(resp.text))

    return session

def run_api_authentication_test(args, test_num, test_total, **obj_args):
    '''Create a session and log into arsenal. Returns a requests session object.'''

    desc = obj_args['test_data']
    url = obj_args['url']
    username = obj_args['username']
    password = obj_args['password']
    expected_response = obj_args['expected_response']

    payload = {
        'login': username,
        'password': password,
    }

    LOG.info('  BEGIN ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))
    session = requests.Session()
    resp = session.post('{0}{1}'.format(args.arsenal_server, url),
                        data=payload,
                        verify=False)
    LOG.info('    Response code: {0}'.format(resp.status_code))
    if not resp.status_code == expected_response:
        LOG.error('    result   : FAIL')
        FAILED_TESTS.append({
            'name': desc,
            'url': url
        })
    else:
        LOG.info('    result   : PASS')

    LOG.info('  END   ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))

@retry(5, HTTPError, ConnectionError, NewConnectionError, RequestException, UnboundLocalError, time_delay=5)
def ar_query(args, endpoint, http_method, data=None, session=None):
    '''Make http requests arsenal.'''

    headers = {'Content-Type': 'application/json'}

    url = '{0}{1}'.format(args.arsenal_server, endpoint)
    LOG.info('    url      : {0}'.format(url))

    try:

        if http_method == 'get':
            LOG.debug('  Submitting get to url: {0}'.format(url))
            resp = requests.get(url,
                                headers=headers,
                                verify=args.ssl_verify)

        if http_method == 'post':
            LOG.info('  Submitting post to url: {0}'.format(url))
            LOG.info('  Data is: {0}'.format(data))
            resp = requests.post(url,
                                 headers=headers,
                                 verify=args.ssl_verify,
                                 json=data)

        if http_method == 'put':
            resp = session.put(url,
                               verify=args.ssl_verify,
                               headers=headers,
                               json=data)

        resp.raise_for_status()
        if resp.status_code == 200:

            try:
                results = resp.json()
            except:
                raise

            LOG.info('    http code: 200')
            LOG.debug(results)

            return results

    except Exception as ex:
        try:
            LOG.error('  API query failed: {0}'.format(ex))
            LOG.error('    text: {0}'.format(resp.text))
        except:
            pass
        raise

def check_key(args, test_num, test_total, obj_type, obj_id, key):
    '''Check a type for a key.'''

    global FAILED_TESTS

    LOG.info('  Testing key ({0:0>3d} of {1:0>3d}): {2}'.format(test_num,
                                                                test_total,
                                                                key))
    url = '/api/{0}/{1}/{2}'.format(obj_type, obj_id, key)
    resp = ar_query(args, url, 'get')
    if resp:
        LOG.debug('    Response data: {0}'.format(resp))
        LOG.info('    result   : PASS')
        return True

    FAILED_TESTS.append({
        'name': key,
        'url': url
    })

def run_basic_endpoint_test(args, test_num, test_total, **obj_args):
    '''Test an endpoint. Gets an object, and then for each key the object
    returns hit that endpoint and ensure that we get a 200 response. Next level
    will be to validate data is as expected.'''

    obj_type = obj_args['endpoint']
    obj_query = obj_args['url']

    global OVERALL_FAIL
    global FAILED_TESTS

    LOG.info('  BEGIN ({0:0>3d} of {1:0>3d}): Testing object '
             'type: {2}'.format(test_num, test_total, obj_type))
    # Get an object to test against
    resp = ar_query(args, obj_query, 'get')
    try:
        my_ob = resp['results'][0]
        my_id = my_ob['id']
        LOG.debug('    Response data: {0}'.format(my_ob))

        # Iterate over all the keys of that object
        sub_test_num = 0
        sub_test_total = len(my_ob)
        for key in my_ob:
            sub_test_num += 1
            if not check_key(args, sub_test_num, sub_test_total, obj_type, my_id, key):
                OVERALL_FAIL = 1
                LOG.error('    result   : FAIL')
    except IndexError:
        LOG.error('    No results returned!')
        OVERALL_FAIL = 1
        FAILED_TESTS.append({
            'name': obj_type,
            'url': obj_query
        })

    LOG.info('  END   ({0:0>3d} of {1:0>3d}): Testing object '
             'type: {2}'.format(test_num, test_total, obj_type))

def check_response_counts(resp, exp_result_count):
    '''Make sure the number of responses matches the count we expect.'''

    global OVERALL_FAIL
    resp_total = resp['meta']['total']

    if not resp_total == exp_result_count:
        LOG.error('      Expected {0} result(s) but got {1} '
                  'instead.'.format(exp_result_count, resp_total))
        LOG.error('      Data: {0}'.format(json.dumps(resp['results'],
                                                      indent=4,
                                                      sort_keys=True)))
        OVERALL_FAIL = 1
        return False
    return True

def check_response_content(resp, exp_responses):
    '''Make sure the number of responses matches the content we expect.'''

    if exp_responses:
        global OVERALL_FAIL
        test_fail = False
        results = resp['results']
        for resp in exp_responses:
            for key, val in resp.items():
                if not any(resp.get(key, None) == val for resp in results):
                    LOG.error('    key error: {0}: {1} expected, but not found in '
                              'results!'.format(key, val))
                    OVERALL_FAIL = 1
                    test_fail = True

        if not test_fail:
            return True
    else:
        LOG.warn('    No expected responses defined for test.')
        return True

def validate_search_test_results(resp, exp_result_count, exp_responses):
    '''Make sure all the search functionality works for all types.'''

    global OVERALL_FAIL

    if not check_response_counts(resp, exp_result_count) or not check_response_content(resp, exp_responses):
        OVERALL_FAIL = 1
        return False
    return True

def run_search_test(args, test_num, test_total, **obj_args):
    '''Make sure all the search functionality works for all types.'''

    desc = obj_args['description']
    url = obj_args['url']
    exp_result_count = obj_args['result_count']
    exp_responses = obj_args['expected_responses']

    LOG.info('  BEGIN ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))
    # Get an object to test against
    resp = ar_query(args, url, 'get')
    LOG.debug('    Response data: {0}'.format(resp))
    if not validate_search_test_results(resp, exp_result_count, exp_responses):
        LOG.error('    result   : FAIL')
        LOG.error('    response : {0}'.format(json.dumps(resp, indent=4,
                                                         sort_keys=True)))
        FAILED_TESTS.append({
            'name': desc,
            'url': url
        })
    else:
        LOG.info('    result   : PASS')

    LOG.info('  END   ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))

def run_node_registration_test(args, test_num, test_total, **obj_args):
    '''Make sure node registration functionality works for all cases.'''

    desc = obj_args['test_data']
    url = obj_args['url']
    data = REGISTER_TEST_CASES[desc]

    LOG.info('  BEGIN ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))
    session = ar_login(args.arsenal_server, 'kaboom', 'password')
    resp = ar_query(args, url, 'put', data=data, session=session)
    LOG.info('    Response data: {0}'.format(resp))
    if not resp['http_status']['code'] == 200:
        LOG.error('    result   : FAIL')
        FAILED_TESTS.append({
            'name': desc,
            'url': url
        })
    else:
        LOG.info('    result   : PASS')

    LOG.info('  END   ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))

def run_parameter_validation_test(args, test_num, test_total, **obj_args):
    '''Make sure you can't ask the api for no parameters or an empty parameter.'''

    desc = obj_args['description']
    url = obj_args['url']
    exp_response = obj_args['expected_response']

    LOG.info('  BEGIN ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))
    resp = ar_query(args, url, 'get')
    LOG.debug('    Response data: {0}'.format(resp))
    if not resp.status_code == exp_response:
        LOG.error('    result   : FAIL')
        LOG.error('    response : {0}'.format(json.dumps(resp, indent=4,
                                                         sort_keys=True)))
        FAILED_TESTS.append({
            'name': desc,
            'url': url
        })
    else:
        LOG.info('    result   : PASS')

    LOG.info('  END   ({0:0>3d} of {1:0>3d}): Testing: {2}'.format(test_num,
                                                                   test_total,
                                                                   desc))

def run_tests(args, desc, call_func, my_tests):
    '''Run all the tests.'''

    separator = '-' * 72

    LOG.info(separator)
    LOG.info('BEGIN: {0}...'.format(desc))
    test_total = len(my_tests)
    for test_num, test_type in enumerate(my_tests):
        test_num += 1
        globals()[call_func](args, test_num, test_total, **test_type)
    LOG.info('END  : {0}.'.format(desc))
    LOG.info(separator)

def check_arsenal_ready(args):
    '''make sure arsenal is ready before proceeding.'''

    LOG.info('Checking to make sure arsenal is ready for queries...')
    ar_query(args, '/api/nodes?name=f', 'get')
    LOG.info('Arsenal is ready.')

def parse_args():
    '''Parse all the command line arguments.'''

    help_desc = '''
    Provisining and management of HP Moonshot chassis.

    >>> api_test.py
    Doing stuff
    '''

    pap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                  description=help_desc)
    pap.add_argument('-a',
                     '--arsenal-server',
                     help='Arsenal server to test against.',
                     default='https://localhost:4443')
    pap.add_argument('-c',
                     '--config-file',
                     help='Configuration file.',
                     default=None)
    pap.add_argument('-d',
                     '--debug',
                     action='store_true',
                     help='Enable debugging.')
    pap.add_argument('-r',
                     '--run-tests',
                     help='Tests to run.',
                     nargs='+',
                     default=['all'])
    pap.add_argument('-s',
                     '--secrets-config',
                     help='Secret config file to use.',
                     default=None)
    pap.add_argument('-S',
                     '--ssl',
                     dest='ssl_verify',
                     help='Whether or not the server is using ssl. Can be True, False, or '
                     'the path to a ca cert',
                     default=False)
    pap.add_argument('-t',
                     '--test-config',
                     help='Yaml config file containing all the tests.',
                     default=None)

    return pap.parse_args()

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
        'arsenal_server',
    ]

    for req in required:
        if not args.__dict__[req]:
            LOG.error('Required option is missing: {0}\n'.format(req))
            sys.exit(2)

def main():
    '''Do all the things.'''

    # parse the args
    args = parse_args()
    configure_logging(args)
    check_req_params(args)

    if args.secrets_config:
        secrets_config = configparser.ConfigParser()
        secrets_config.read(args.secrets_config_file)

        username = secrets_config.get('arsenal', 'username')
        password = secrets_config.get('arsenal', 'password')

    # Read in the config file
    yaml = YAML()
    with open(args.test_config, 'r') as config_fd:
        test_config = yaml.load(config_fd)

    check_arsenal_ready(args)

    LOG.info('Beginning tests...')

    tests_to_run = []
    if 'all' in args.run_tests:
        tests = test_config['tests']
    else:
        tests = args.run_tests

    for test in tests:
        tests_to_run.append(test_config['tests'][test])

    for test_type in tests_to_run:
        run_tests(args, test_type['description'], test_type['function'], test_type['tests'])

    overall_msg = 'SUCCESS'
    if OVERALL_FAIL != 0:
        overall_msg = 'FAILURE'

    LOG.info('All tests complete, overall result is: {0}'.format(overall_msg))

    if FAILED_TESTS:
        LOG.error('Failed tests:')
        LOG.error('-' * 72)
        for test in FAILED_TESTS:
            LOG.error('  name  : {0}'.format(test['name']))
            LOG.error('    url : {0}'.format(test['url']))
        LOG.error('-' * 72)

    sys.exit(OVERALL_FAIL)

if __name__ == '__main__':
    main()
