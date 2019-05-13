# pylint: disable=too-many-lines
'''Arsenal client library'''
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
import os
import sys
import ConfigParser
import logging
import subprocess
import json
from argparse import Namespace
import re
import requests
from arsenalclient.arsenal_facts import ArsenalFacts
from arsenalclient.authorization import Authorization
from arsenalclient.authorization import check_root

# Log handling
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except (ImportError, AttributeError):
    pass

LOG = logging.getLogger(__name__)

logging.VERBOSE = 11
logging.addLevelName(logging.VERBOSE, "VERBOSE")
def verbose(self, message, *args, **kws):
    '''Set custom logging level for more logging information than info but less
    than debug.'''

    if self.isEnabledFor(logging.VERBOSE):
        self._log(logging.VERBOSE, message, args, **kws)
logging.Logger.verbose = verbose

# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass


# pylint: disable=R0904
class Client(object):
    '''The arsenal client library.

    Usage:

      >>> from arsenalclient.client import Client
      >>> client = Client('/path/to/my/arsenal.ini', '/path/to/my/secret/arsenal.ini')
      >>> tags = [
      ...     'tag1=value1',
      ... ]
      >>> results = client.object_search('nodes', 'name=myserver,status=inservice', True)
      >>> resp = client.tag_assignments(tags, 'nodes', results, 'put')
      INFO    - Command successful.
      INFO    - Assigning tag: tag1=value1
      INFO    -   nodes: myserver1.mycompany.com
      INFO    - Command successful.
      INFO    - Command successful.
      INFO    - Assigning tag: tag1=value1
      INFO    -   nodes: myserver2.mycompany.com
      INFO    - Command successful.

    Args:

        conf       : A string representing the path to the conf file.
        secret_conf: An optional string representing the path to the
            secret_conf file. The secret_conf is only needed if you are calling arsenal
            from a script and need to pass a username and password.

        args       : An optional namespace object passed from a cli. Keys defined in
            args override any settings in the config file.
    '''

    def __init__(self,
                 conf_file,
                 secret_conf_file=None,
                 args=None
                ):

        self.conf_file = conf_file
        self.secret_conf_file = secret_conf_file
        self.args = args
        self.session = requests.session()
        self.cookies = None
        self.init_log_lines = []

        self.settings = Namespace()
        self.settings.api_host = None
        self.settings.api_protocol = None
        self.settings.conf = None
        self.settings.cookie_file = None
        self.settings.log_file = None
        self.settings.log_level = None
        self.settings.user_login = None
        self.settings.user_password = None
        self.settings.verify_ssl = None

        self.load_config()
        self.init_logging()
        self.login_overrides()
        self.arsenal_facts = ArsenalFacts()
        self.authorization = Authorization(api_host=self.settings.api_host,
                                           api_protocol=self.settings.api_protocol,
                                           cookie_file=self.settings.cookie_file,
                                           user_login=self.settings.user_login,
                                           user_password=self.settings.user_password,
                                           verify_ssl=self.settings.verify_ssl)

    def load_config(self):
        '''Read in all our configuration settings from the main .ini and from the
        secrets.ini, if specified. Also stores init_log_lines to be logged
        after logging is fully configured. Also sets any overrides from args,
        if they were provided.
        '''

        conf_parse = ConfigParser.ConfigParser()
        conf_parse.read(self.conf_file)
        for section in conf_parse.sections():
            for key, val in conf_parse.items(section):
                if val:
                    self.init_log_lines.append('Assigning setting: {0}={1}'.format(key,
                                                                                   val))
                    setattr(self.settings, key, val)

        if self.secret_conf_file:
            secret_conf_parse = ConfigParser.SafeConfigParser()
            secret_conf_parse.read(self.secret_conf_file)
            for key, val in secret_conf_parse.items('user'):
                if val:
                    if key == 'user_password':
                        self.init_log_lines.append('Assigning secret setting: '
                                                   '{0}=HIDDEN'.format(key))
                    else:
                        self.init_log_lines.append('Assigning secret setting: '
                                                   '{0}={1}'.format(key, val))
                    setattr(self.settings, key, val)

        # Override from args if present
        if self.args:
            for arg in vars(self.args):
                if getattr(self.args, arg):
                    self.init_log_lines.append('Assigning arg: '
                                               '{0}={1}'.format(arg,
                                                                getattr(self.args,
                                                                        arg)))
                    setattr(self.settings, arg, getattr(self.args, arg))

        # Have to do this becasue it can be a boolean or a string.
        if self.settings.verify_ssl == 'True':
            self.settings.verify_ssl = bool(self.settings.verify_ssl)

        if self.settings.verify_ssl == 'False':
            self.settings.verify_ssl = bool('')

    def login_overrides(self):
        '''Sets user_login to read_only if no login is defined.'''

        if not getattr(self.settings, 'user_login', None):
            LOG.debug('No user_login defined, setting to: read_only')
            setattr(self.settings, 'user_login', 'read_only')

    def init_logging(self):
        '''Configure logging and log settings and any overrides, if present.'''

        if self.settings.log_level:
            self.settings.log_level = getattr(logging, self.settings.log_level)
        else:
            self.settings.log_level = logging.INFO

        if getattr(self.settings, 'verbose', None):
            self.settings.log_level = logging.VERBOSE
        elif getattr(self.settings, 'debug', None):
            self.settings.log_level = logging.DEBUG
        elif getattr(self.settings, 'quiet', None):
            self.settings.log_level = logging.ERROR

        # Set up logging to file
        if getattr(self.settings, 'write_log', None):

            logging.basicConfig(level=self.settings.log_level,
                                format='%(asctime)s %(levelname)-8s- %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=self.settings.log_file,
                                filemode='a')

        root = logging.getLogger()
        root.setLevel(self.settings.log_level)

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(self.settings.log_level)
        format_msg = '%(levelname)-8s- %(message)s'
        if getattr(self.settings, 'timestamps', None):
            format_msg = '%(asctime)s %(levelname)-8s- %(message)s'
        formatter = logging.Formatter(format_msg)
        console.setFormatter(formatter)
        root.addHandler(console)

        # log our overrides now that logging is configured.
        for line in self.init_log_lines:
            LOG.debug(line)

        if getattr(self.settings, 'write_log', None):
            LOG.info('Messages are being written to the log file: '
                     '{0}'.format(self.settings.log_file))

        LOG.debug('Using server: {0}'.format(self.settings.api_host))

    @staticmethod
    def check_response_codes(resp, log_success=True):
        '''Checks the response codes and logs appropriate messaging for the client.

        Args:
            resp: A response object from the requests package.

        Returns:
            Json from response if successful, json formatted response code otherwise.
        '''

        try:
            if resp.status_code == 200:
                if log_success:
                    LOG.info('Command successful.')
            else:
                LOG.warn('{0}: {1}'.format(resp.status_code, resp.reason))
            LOG.debug('Returning json...')
            return resp.json()
        except ValueError:
            LOG.debug('Json decode failed, falling back to manual json response...')
            my_resp = {
                'http_status': {
                    'code': resp.status_code,
                    'message': resp.reason,
                }
            }
            return my_resp

    def api_conn(self, request, data=None, method='get', log_success=True):
        ''' Manages http requests to the API.

        Usage:

            >>> data = {'unique_id': '12345'}
            >>> api_conn('/api/nodes/1')
            <{json object}>
            >>> api_conn('/api/nodes', data, 'put')
            <{json object}>
            >>> api_conn('/api/nodes', data, 'delete')
            <{json object}>
            >>> api_conn('/api/nodes', data, 'get_params')
            <{json object}>
            >>> api_conn('/api/invalid', data, 'get_params')
            <Response 404>

        Args:
            request (str): The uri endpoint to request.
            data (dict): A dict of paramters to send with the http request.
            method (str): The http method to use. Valid choices are:
                put
                delete
                get_params
                delete

        Returns:
            check_response_codes()
        '''

        headers = {'content-type': 'application/json'}

        api_url = '{0}://{1}{2}'.format(self.settings.api_protocol,
                                        self.settings.api_host,
                                        request)

        try:
            if method == 'put':

                self.authorization.get_cookie_auth()

                LOG.verbose('PUT API call to endpoint: {0}'.format(api_url))
                LOG.verbose('PUT params: \n{0}'.format(json.dumps(data,
                                                                  indent=2,
                                                                  sort_keys=True)))

                resp = self.session.put(api_url,
                                        verify=self.settings.verify_ssl,
                                        cookies=self.authorization.cookies,
                                        headers=headers,
                                        json=data)

                # re-auth if our cookie is invalid/expired
                if resp.status_code == 401:
                    LOG.debug('Recieved 401 from api, re-authenticating...')
                    self.authorization.authenticate()
                    resp = self.session.put(api_url,
                                            verify=self.settings.verify_ssl,
                                            cookies=self.authorization.cookies,
                                            headers=headers,
                                            json=data)

                return self.check_response_codes(resp)

            elif method == 'delete':

                self.authorization.get_cookie_auth()

                LOG.verbose('DELETE API call to endpoint: {0}'.format(api_url))
                LOG.verbose('DELETE params: \n{0}'.format(json.dumps(data,
                                                                     indent=2,
                                                                     sort_keys=True,)))

                resp = self.session.delete(api_url,
                                           verify=self.settings.verify_ssl,
                                           cookies=self.authorization.cookies,
                                           headers=headers,
                                           json=data)

                # re-auth if our cookie is invalid/expired
                if resp.status_code == 401:
                    LOG.debug('Recieved 401 from api, re-authenticating...')
                    self.authorization.authenticate()
                    resp = self.session.delete(api_url,
                                               verify=self.settings.verify_ssl,
                                               cookies=self.authorization.cookies,
                                               headers=headers,
                                               json=data)

                return self.check_response_codes(resp)

            elif method == 'get_params':
                LOG.verbose('GET API call to endpoint (with params): {0}'.format(api_url))
                LOG.verbose('GET params: \n{0}'.format(json.dumps(data,
                                                                  indent=2,
                                                                  sort_keys=True,)))

                resp = self.session.get(api_url,
                                        verify=self.settings.verify_ssl,
                                        params=data)

                return self.check_response_codes(resp, log_success=log_success)

            else:
                LOG.verbose('GET API call to endpoint: {0}'.format(api_url))

                resp = self.session.get(api_url,
                                        verify=self.settings.verify_ssl)

                return self.check_response_codes(resp, log_success=log_success)

        except requests.exceptions.ConnectionError:
            LOG.error('Unable to connect to server: {0}'.format(self.settings.api_host))
            raise

    # pylint: disable=R0913
    def object_search(self, object_type, search, fields=None, exact_get=None, exclude=None):
        '''Main search function to query the API. Parses key=value args passed
        from the cli before querying the API.

        Usage:

          >>> client.object_search('nodes', 'name=myserver,unique_id=1234', exact_get=True)
          <Response [200]>
          >>> client.object_search('nodes', 'name=invalid', exact_get=True)
          <Response [404]>

        Args:
            object_type (str): The type of object we are searching for (nodes,
                node_groups, statuses, etc.)
            search (str): The key=value search terms. Multiple values separated
                by comma (,). Multiple keys sparated by comma (,).
            exact_get (str): Whether to search for terms exactly or use wildcard
                matching.
            exclude (str): The key=value search terms to explicitly exclude. Multiple
                values separated by comma (,). Multiple keys sparated by comma (,).

        Returns:
            A a list containing dicts of search results.
        '''

        regex = re.compile(r'([^=]+)=([^=]+)(?:,|$)')
        matches = regex.findall(search)
        data = {}
        for match in matches:
            data[match[0]] = match[1]

        if exclude:
            ex_matches = regex.findall(exclude)
            for match in ex_matches:
                data['ex_{0}'.format(match[0])] = match[1]

        data['exact_get'] = exact_get
        if fields:
            data['fields'] = fields

        api_endpoint = '/api/{0}'.format(object_type)
        resp = self.api_conn(api_endpoint, data, method='get_params', log_success=False)

        LOG.debug('Results are: {0}'.format(json.dumps(resp,
                                                       indent=2,
                                                       sort_keys=True)))
        if not resp['results']:
            LOG.info('No results found for search.')

        return resp

    def get_audit_history(self, results, audit_type=None):
        '''Retrieve audit history for a list of search results. Returns an
        updated list with audit history attached.'''

        resp = []
        for obj in results:
            my_audit = self.api_conn('/api/{0}_audit/{1}'.format(audit_type, obj['id']),
                                     log_success=False)
            obj['audit_history'] = my_audit['results']
            resp.append(obj)

        return resp

    ## HARDWARE_PROFILES
    def hardware_profile_collect(self):
        '''Collect all the information about the node's hardware_profile. Used
        for node registration.'''

        resp = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'name': 'Unknown',
        }

        self.arsenal_facts.resolve()
        facts = self.arsenal_facts.facts

        try:
            resp['manufacturer'] = facts['hardware']['manufacturer']
            resp['model'] = facts['hardware']['product_name']
            resp['name'] = facts['hardware']['name']
        except KeyError:
            LOG.error('Unable to determine hardware_profile.')

        return resp

    ## OPERATING SYSTEMS
    def operating_system_collect(self):
        '''Collect all the information about the node's operating_system. Used
        for node registration.'''

        resp = {
            'name': 'Unknown',
            'variant': 'Unknown',
            'version_number': 'Unknown',
            'architecture': 'Unknown',
            'description': 'Unknown',
        }

        self.arsenal_facts.resolve()
        facts = self.arsenal_facts.facts

        try:
            resp['name'] = facts['os']['name']
            resp['variant'] = facts['os']['variant']
            resp['version_number'] = facts['os']['version_number']
            resp['architecture'] = facts['os']['architecture']
            resp['description'] = facts['os']['description']
        except KeyError:
            LOG.error('Unable to determine operating_system.')

        return resp

    ## NODES
    def node_get_unique_id(self):
        '''Determines the unique_id of a node and returns it as a string.'''

        if not check_root():
            return None

        LOG.debug('Determining unique_id...')
        facts = self.arsenal_facts.facts

        if facts['os']['kernel'] == 'Linux' or facts['os']['kernel'] == 'FreeBSD':
            if facts['hardware']['virtual'] == 'kvm':
                unique_id = facts['networking']['mac_address']
                LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
            elif facts['ec2']['instance_id']:
                unique_id = facts['ec2']['instance_id']
                LOG.debug('unique_id is from ec2 instance_id: {0}'.format(unique_id))
            elif os.path.isfile('/usr/sbin/dmidecode'):
                unique_id = self.node_get_uuid()
                if unique_id:
                    LOG.debug('unique_id is from dmidecode: {0}'.format(unique_id))
                else:
                    unique_id = facts['networking']['mac_address']
                    LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
            else:
                unique_id = facts['networking']['mac_address']
                LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
        else:
            unique_id = facts['networking']['mac_address']
            LOG.debug('unique_id is from mac address: {0}'.format(unique_id))

        return unique_id

    @staticmethod
    def node_get_uuid():
        '''Gets the uuid of a node from dmidecode if applicable.'''

        unique_id = None
        file_null = open(os.devnull, 'w')
        proc = subprocess.Popen(['/usr/sbin/dmidecode', '-s', 'system-uuid'],
                                stdout=subprocess.PIPE,
                                stderr=file_null)
        proc.wait()
        uuid = proc.stdout.readlines()
        # Work around bad UUIDs
        bogus_uuids = [
            '03000200-0400-0500-0006-000700080009',
            'Not Settable',
        ]
        if uuid:
            strip_uuid = uuid[-1].rstrip()
            if strip_uuid in bogus_uuids:
                LOG.warn('unique_id from dmidecode is known bad: {0}'.format(strip_uuid))
            else:
                unique_id = strip_uuid
        else:
            # Support older versions of dmidecode
            proc = subprocess.Popen(['/usr/sbin/dmidecode', '-t', '1'], stdout=subprocess.PIPE)
            proc.wait()
            dmidecode_out = proc.stdout.readlines()
            xen_match = "\tUUID: "
            for line in dmidecode_out:
                if re.match(xen_match, line):
                    strip_uuid = line[7:].rstrip()
                    if strip_uuid in bogus_uuids:
                        LOG.warn('unique_id from dmidecode is known bad: {0}'.format(strip_uuid))
                    else:
                        unique_id = strip_uuid

        return unique_id

    def node_collect(self):
        '''Collect all data about a node for registering with the server.'''

        LOG.debug('Collecting data for node.')

        resp = {}
        resp['network_interfaces'] = []
        resp['data_center'] = {}
        resp['guest_vms'] = []
        resp['ec2'] = None

        self.arsenal_facts.resolve()
        facts = self.arsenal_facts.facts

        resp['name'] = facts['networking']['fqdn']
        unique_id = self.node_get_unique_id()
        resp['unique_id'] = unique_id

        resp['hardware_profile'] = self.hardware_profile_collect()

        resp['operating_system'] = self.operating_system_collect()

        resp['data_center']['name'] = facts['data_center']['name']

        if facts['ec2']['instance_id']:
            LOG.debug('This is an Ec2 instance.')
            resp['ec2'] = facts['ec2']

        resp['uptime'] = facts['uptime']

        if facts['hardware']['serial_number']:
            resp['serial_number'] = facts['hardware']['serial_number']
        if facts['processors']['count']:
            resp['processor_count'] = facts['processors']['count']

        for net_if in facts['networking']['interfaces']:
            my_attribs = facts['networking']['interfaces'][net_if]
            # Use the node's unqiue_id prefixed with the interface name if it
            # doesn't have a mac address of it's own (bond, sit, veth, etc.).
            if not 'unique_id' in my_attribs:
                uid = '{0}_{1}'.format(net_if, unique_id)
                my_attribs['unique_id'] = uid
            # Set the bond IP on it's slaves too.
            else:
                my_master = my_attribs.get('bond_master')
                if my_master:
                    try:
                        my_ip = facts['networking']['interfaces'][my_master]['ip_address']
                        my_attribs['ip_address'] = my_ip
                    except KeyError:
                        pass
            my_attribs['name'] = net_if
            resp['network_interfaces'].append(my_attribs)

        if facts['guest_vms']:
            resp['guest_vms'] = facts['guest_vms']

        return resp

    def node_delete(self, node):
        '''Delete a node object from the server.

        Args:

            node: A node dictionary to delete. Must contain the
                node name, id, and unique_id.

        Usage:

          >>> client.data_center_delete(<data_center_dictionary>)
          <Response [200]>
        '''

        LOG.info('Deleting node name: {0} unique_id: {1}'.format(node['name'],
                                                                 node['unique_id']))

        return self.api_conn('/api/nodes/{0}'.format(node['id']), method='delete')

    def node_register(self):
        '''Collect all the data about a node and register it with the server. '''

        if check_root():
            LOG.debug('Overriding login for node registration to: kaboom')
            self.authorization.user_login = 'kaboom'
            my_cookie = '/root/.{0}_kaboom_cookie'.format(self.settings.api_host)
            LOG.debug('Overriding setting for user kaboom: '
                      'cookie_file={0}'.format(my_cookie))
            self.authorization.cookie_file = my_cookie
            node = self.node_collect()

            LOG.info('Registering node name: {0} unique_id: {1}'.format(node['name'],
                                                                        node['unique_id']))
            resp = self.api_conn('/api/register', node, method='put')

            return resp

    def node_enc(self, name, param_sources=None):
        '''Run the puppet node enc. Returns a dict.

        Args:

            name         : The fqdn of the node (required)
            param_sources: A boolean that controls whether or not to return
                data about what level of the hierarchy each variable comes from.
                Defaults to False.
        '''

        LOG.verbose('Running puppet ENC for node name: {0}'.format(name))

        data = {
            'name': name,
        }

        if param_sources:
            data['param_sources'] = True

        resp = self.api_conn('/api/enc', data, method='get_params', log_success=False)

        return resp

    def node_create(self, unique_id, name, status_id, hw_id=1, os_id=1):
        '''Create a new node based on provided prameters normally collected
        automatically during a register operation.

        Args:

            unique_id: The unique_id of the node to create.
            name     : The name of the node to create.
            status_id: The status_id of the status to assign to the node.

        Usage:

            >>> client.node_create('12345', 'myserver.mycompany.com', '1')
            <Response [200]>
        '''

        node = {
            'unique_id': unique_id,
            'name': name,
            'status_id': status_id,
            'operating_system': {
                'id': os_id,
            },
            'hardware_profile': {
                'id': hw_id,
            },
        }

        LOG.info('Submitting new node name: {0} unique_id: {1} '
                 'status_id: {2} hardware_profile_id: {3} operating_system_id: '
                 '{4}'.format(name, unique_id, status_id, hw_id, os_id))

        return self.api_conn('/api/nodes', node, method='put')

    def node_set_status(self, status_name, nodes):
        '''Set the status of one or more nodes.

        Args:

            status_name: The name of the status you wish to set the node to.
            nodes      : The nodes from the search results to set the status to.

        Usage:

            >>> client.node_set_status('inservice', <object_search results>)
            <Response [200]>
        '''
        status = self.status_find_by_name(status_name)

        node_ids = []
        for node in nodes:
            node_ids.append(node['id'])

        LOG.info('Assigning status: {0}'.format(status['name']))

        for node in nodes:
            LOG.info('  node: {0}'.format(node['name']))

        data = {'nodes': node_ids}

        return self.api_conn('/api/statuses/{0}/nodes'.format(status['id']), data, method='put')

    ## NODE_GROUPS
    def node_group_find_by_name(self, name):
        '''Find a node_group by name.'''

        data = {'name': name,
                'exact_get': True,
               }

        try:
            resp = self.api_conn('/api/node_groups', data, method='get_params', log_success=False)
            results = resp['results'][0]
            return results
        except IndexError:
            LOG.warn('node_group: {0} not found'.format(name))
            raise

    def node_group_create(self, name, owner, description, notes_url):
        '''Create a new node_group.

        Args:
            name       : The name of the node_group you wish to create.
            owner      : The email address of the owner of the node group.
            description: A text description of the members of this node_group.
            notes_url  : A url to documentation relevant to the node_group.

        Usage:

            >>> client.create_node_group('my_node_group',
            ...                          'email@mycompany.com',
            ...                          'The nodegroup for all the magical servers',
            ...                          'https://somurl.somedomain.com/')
            <Response [200]>
        '''

        data = {
            'name': name,
            'owner': owner,
            'description': description,
            'notes_url': notes_url,
        }

        LOG.info('Creating node_group name: {0} owner: {1} '
                 'description: {2} notes_url: {3}'.format(name,
                                                          owner,
                                                          description,
                                                          notes_url))


        return self.api_conn('/api/node_groups', data, method='put')

    def node_group_delete(self, node_group):
        '''Delete an existing node_group.

        Args:

            node_group: A node_group dictionary to delete.

        Usage:

          >>> client.delete_node_group(<node_group_dictionary>)
          <Response [200]>
        '''

        LOG.info('Deleting node_group name: {0} id: {1}'.format(node_group['name'],
                                                                node_group['id']))
        return self.api_conn('/api/node_groups/{0}'.format(node_group['id']), method='delete')

    def node_group_a_d(self, node_group, nodes, api_method):
        '''Assign or de-assign node_group to a list of node objects.'''

        node_names = []
        node_ids = []
        msg = 'Assigning'
        if api_method == 'delete':
            msg = 'De-assigning'

        for node in nodes:
            node_names.append(node['name'])
            node_ids.append(node['id'])

        LOG.info('{0} node_group: {1}'.format(msg,
                                              node_group['name']))
        for node in node_names:
            LOG.info('  node: {0}'.format(node))

        data = {'nodes': node_ids}

        return self.api_conn('/api/node_groups/{0}/nodes'.format(node_group['id']),
                             data,
                             method=api_method)

    def node_group_assign(self, name, nodes):
        '''Assign a node_group to one or more nodes.

        name : The name of the node_group to assign to the node search results.
        nodes: The nodes from the search results to assign to the node_group.

        Usage:

          >>> client.node_group_assign('node_group1', <object_search results>)
          <json>
        '''

        try:
            node_group = self.node_group_find_by_name(name)
            return self.node_group_a_d(node_group, nodes, 'put')
        except IndexError:
            pass

    def node_group_deassign(self, name, nodes):
        '''De-assign a node_group from one or more nodes.

        name : The name of the node_group to de-assign from the node search results.
        nodes: The nodes from the search results to de-assign from the node_group.

        Usage:

          >>> client.node_group_deassign('node_group1', <object_search results>)
          <json>
        '''

        try:
            node_group = self.node_group_find_by_name(name)
            return self.node_group_a_d(node_group, nodes, 'delete')
        except IndexError:
            pass

    def node_groups_deassign_all(self, nodes):
        '''De-assign ALL node_groups from one or more nodes.

        nodes: The nodes from the search results to de-assign from the node_group.

        Usage:

          >>> client.node_groups_deassign_all(<object_search results>)
          <json>
        '''

        node_ids = []
        for node in nodes:
            LOG.info('Removing all node_groups from node: {0}'.format(node['name']))
            node_ids.append(node['id'])

        data = {'node_ids': node_ids}

        try:
            resp = self.api_conn('/api/bulk/node_groups/deassign',
                                 data,
                                 method='delete')
        except Exception as ex:
            LOG.error('Command failed: {0}'.format(repr(ex)))
            raise

        return resp

    ## STATUSES
    def status_create(self, name=None, **kwargs):
        '''Create a new status.

        Required args:

            name       : The name of the status you wish to create.
            description: A text description of status.

        Usage:
            >>> client.status_create('my_status',
            ...                      'The status to rule them all.')
            <Response [200]>
        '''

        kwargs['name'] = name

        return self.api_conn('/api/statuses', kwargs, method='put')

    def status_find_by_name(self, status_name):
        '''Find a status on the server by name. Returns a dict of the status if
        found, None otherwise.'''

        data = {
            'name': status_name,
            'exact_get': True,
        }
        try:
            resp = self.api_conn('/api/statuses', data, method='get_params', log_success=False)
            return resp['results'][0]
        except IndexError:
            LOG.warn('Status not found: {0}'.format(status_name))
            return None

    ## TAGS
    def tag_create(self, tag_name, tag_value):
        '''Create a new tag.

        Args:
            tag_name : The name of the tag you wish to create.
            tag_value: The value of the tag you wish to create.

        Usage:

            >>> client.tag_create('my_key',
            ...                   'my_value')
            <Response [200]>
        '''

        data = {
            'name': tag_name,
            'value': tag_value,
        }
        LOG.info('Creating new tag: {0}={1}'.format(tag_name, tag_value))
        resp = self.api_conn('/api/tags', data, method='put')
        try:
            data['id'] = resp['id']
            return data
        except KeyError:
            return resp

    def tag_delete(self, tags):
        '''Delete one or more existing tags.

        Args:

            tags: A list of tag dictionaries to delete. Each Dictionary must
            contain the following keys:

                id
                name
                value

        Usage:

          >>> client.tag_delete(<tag_dictionary_list>)
          {u'id': 739, u'value': u'myvalue', u'name': u'mytag'}
        '''

        del_tags = []
        for tag in tags:
            LOG.info('Deleting tag '
                     'id={0},tag: {1}={2}'.format(tag['id'],
                                                  tag['name'],
                                                  tag['value']))

            resp = self.api_conn('/api/tags/{0}'.format(tag['id']),
                                 method='delete')
            del_tags.append(resp)

        return del_tags

    def tag_get_by_name_value(self, tag_name, tag_value):
        '''Get a tag from the server based on it's specific name and value.'''

        LOG.debug('Searching for tag name: {0} value: {1}'.format(tag_name,
                                                                  tag_value))
        data = {
            'name': tag_name,
            'value': tag_value,
            'exact_get': True,
        }
        resp = self.api_conn('/api/tags', data, method='get_params', log_success=False)
        LOG.debug('Response is: {0}'.format(resp))

        return resp

    def tag_assignments(self, tags, object_type, results, api_method):
        '''Assign or de-assign a list of tags to a list of node, node_group, or
        data_center objects.

        Args:

            tag        : A list of tags in the format of key=value to assign to the
                node, node_group, or data_center search results.
            object_type: A string representing the object_type to assign the
                tag to. One of nodes, node_groups or data_centers.
            results    : The nodes, node_groups, or data_centers from the results
                of self.object_search() to assign the tag to.
            api_method : A string representing whether or not to put (assign)
                or delete (deassign) the tags from the self.object_search() results.

        Returns:

            A dictionary of tag id's and the responses from the server from
            each request.

        Usage:

          >>> resp = client.object_search('nodes', 'name=tst0000')
          >>> results = resp['results']
          >>> tags = [
          ...     'cli1=value1',
          ...     'cli2=value2',
          ... ]

          Assigning:

          >>> resp = client.tag_assignments(tags, 'nodes', results, 'put')
          INFO    - Command successful.
          INFO    - Assigning tag: cli1=value1
          INFO    -   nodes: tst0000.server
          INFO    - Command successful.
          INFO    - Command successful.
          INFO    - Assigning tag: cli2=value2
          INFO    -   nodes: tst0000.server
          INFO    - Command successful.

          De-assigning:

          >>> resp = client.tag_assignments(tags, 'nodes', results, 'delete')
          INFO    - De-assigning tag: cli1=value1
          INFO    -   nodes: fopd-tst0058.server
          INFO    - Command successful.
          INFO    - De-assigning tag: cli2=value2
          INFO    -   nodes: fopd-tst0058.server
          INFO    - Command successful.
        '''

        action_names = []
        action_ids = []
        msg = 'Assigning'
        if api_method == 'delete':
            msg = 'De-assigning'

        for action_object in results:
            action_names.append(action_object['name'])
            action_ids.append(action_object['id'])

        for tag in tags:
            tag_name, tag_value = tag.split('=')
            resp = self.tag_get_by_name_value(tag_name, tag_value)
            if not resp['results']:
                if api_method == 'delete':
                    LOG.debug('Tag not found, nothing to do.')
                    continue
                else:
                    LOG.debug('Tag not found, creating...')
                    resp = self.tag_create(tag_name, tag_value)

            if resp['http_status'].get('code') == 200:
                this_tag = resp['results'][0]
                LOG.info('{0} tag: {1}={2}'.format(msg,
                                                   this_tag['name'],
                                                   this_tag['value']))
                for action_name in action_names:
                    LOG.info('  {0}: {1}'.format(object_type, action_name))

                data = {object_type: action_ids}

                try:
                    resp = self.api_conn('/api/tags/{0}/{1}'.format(this_tag['id'], object_type),
                                         data,
                                         method=api_method)
                except:
                    raise

        return resp

    ## DATA_CENTERS
    def data_center_create(self, name=None, **kwargs):
        '''Create a new data_center or update an existing one.

        Required args:

            name: A string that is name of the data_center you
                wish to create.

        Optional args:

            address_1   : A string that is address line 1.
            address_2   : A string that is address line 2.
            admin_area  : A string that is the address state/province.
            city        : A string that is the address city.
            contact_name: A string that is the data center contact name.
            country     : A string that is the address country.
            phone_number: A string that is data center contact phone number.
            postal_code : A string that is the address postal (zip) code.
            provider    : A string that is the name of the data center
                provider (ex: SoftLayer, Switch, EC2, GCP, etc.)

        Usage:

            >>> data = {'provider': 'Ec2'}
            >>> client.data_center_create(name='usw1',
            ...                           **data)
            <Response [200]>
        '''

        LOG.info('Submitting data_center: {0}'.format(name))

        if 'status' in kwargs:
            status = self.status_find_by_name(kwargs['status'])
            del kwargs['status']
            kwargs['status_id'] = status['id']

        try:
            kwargs['name'] = name
            data_center = self.api_conn('/api/data_centers',
                                        kwargs,
                                        method='put')
        except Exception as ex:
            LOG.error('Command failed: {0}'.format(repr(ex)))
            raise

        return data_center

    def data_center_delete(self, data_center):
        '''Delete an existing data_centers.

        Args:

            data_center: A data_center dictionary to delete. Must contain the
                data_center name and id.

        Usage:

          >>> client.data_center_delete(<data_center_dictionary>)
          <Response [200]>
        '''

        LOG.info('Deleting data_center name: {0} id: {1}'.format(data_center['name'],
                                                                 data_center['id']))

        return self.api_conn('/api/data_centers/{0}'.format(data_center['id']), method='delete')
