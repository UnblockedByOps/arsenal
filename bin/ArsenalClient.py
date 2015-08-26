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
import subprocess
import re
import logging
import ConfigParser
import json
import yaml
import collections
import types
import getpass
import ast
import requests

logging.basicConfig()
log = logging.getLogger(__name__)
# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
# FIXME: ssl issues
requests.packages.urllib3.disable_warnings()
session = requests.session()


class ArsenalClient(object):
    """The main arsenal cleint class"""
    def __init__(self,
                 conf_file = None,
                 secrets_file = None,
                 args = None):
        self.conf_file = conf_file
        self.secrets_file = secrets_file
        self.args = args
        self.log = logging.getLogger(__name__)

        # FIXME: Should we write to the log file at INFO even when console is ERROR?
        # FIXME: Should we write to a log at all for regular users? Perhaps only if they ask for it i.e another option?
        if args.verbose:
            log_level = logging.DEBUG
        elif args.quiet:
            log_level = logging.ERROR
        else:
            log_level = logging.INFO

        # Set up logging to file
        if args.write_log:

            logging.basicConfig(level=log_level,
                                format='%(asctime)s %(levelname)-8s- %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=self.log_file,
                                filemode='a')

        root = logging.getLogger()
        root.setLevel(log_level)

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(log_level)
        formatter = logging.Formatter('%(levelname)-8s- %(message)s')
        console.setFormatter(formatter)
        root.addHandler(console)

        if args.verbose:
            log.info('Debug messages are being written to the log file : %s'
                     % self.log_file)

        log.info('Using server: {0}'.format(self.api_host))


    @classmethod
    def set_config(cls, config_file, secrets_config_file = None, args = None):

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        # User overridable
        try:
            cls.api_host = args.api_host
        except:
            cls.api_host = config.get('main', 'api.host')

        try:
            cls.login = args.login
        except:
            cls.login = config.get('main', 'api.login')

        try:
            cls.cookie_file = args.cookie_file
        except:
            cls.cookie_file = config.get('main', 'api.cookie_file')

        # Config file only
        cls.api_protocol = config.get('main', 'api.protocol')
        cls.ca_bundle_file = config.get('main', 'ca.bundle.file')
        cls.verify_ssl = bool(config.get('main', 'verify.ssl'))
        cls.log_file = config.get('main', 'log.file')

        if cls.login == 'kaboom':
            check_root(cls.login)
            # FIXME: Will need os checking here
            cls.cookie_file = '/root/.arsenal_kaboom_cookie'
    
        if cls.login == 'hvm':
            check_root(cls.login)
            # FIXME: Will need os checking here
            cls.cookie_file = '/root/.arsenal_hvm_cookie'

        # This is only needed on hypervisors
        if secrets_config_file:
            try:
                secrets_config = ConfigParser.ConfigParser()
                secrets_config.read(secrets_config_file)
                # FIXME: should be in passwords section
                cls.hvm_password = secrets_config.get('main', 'hvm.password')
            except:
#                log.error('Secrets file missing or malformed!')
                sys.exit(1)



    def get_cookie_auth(self):
        """Gets cookies from cookie file or authenticates if no cookie file
           is present"""
    
        try:
            cookies = self.read_cookie()
            if not cookies:
                cookies = self.authenticate()
            else:
                cookies = ast.literal_eval(cookies)
    
            return cookies
    
        except Exception, e:
            log.error('Failed: %s' % e)
    
    
    def read_cookie(self):
        """Reads cookies from cookie file"""
    
        log.debug('Checking for cookie file: %s' % (self.cookie_file))
        if os.path.isfile(self.cookie_file):
            log.debug('Cookie file found: %s' % (self.cookie_file))
            with open(self.cookie_file, 'r') as contents:
                cookies = contents.read()
            return cookies
        else:
            log.debug('Cookie file does not exist: %s' % (self.cookie_file))
            return None
    
    
    def write_cookie(self, cookies):
        """Writes cookies to cookie file"""
    
        log.info('Writing cookie file: %s' % (self.cookie_file))
    
        try:
            cd = dict(cookies)
            with open(self.cookie_file, "w") as cf:
                cf.write(str(cd))
            os.chmod(self.cookie_file, 0600)
    
            return True
        except Exception as e:
            log.error('Unable to write cookie: %s' % self.cookie_file)
            log.error('Exception: %s' % e)


    def authenticate(self):
        """Prompts for user password and authenticates against the API.
           Writes response cookies to file for later use."""
    
        log.info('Authenticating login: %s' % (self.login))
        if self.login == 'kaboom':
            password = 'password'
        elif self.login == 'hvm':
            password = self.hvm_password
        else:
            password = getpass.getpass('password: ')
    
        try:
            payload = {'form.submitted': True,
                       'api.client': True,
                       'return_url': '/api',
                       'login': self.login,
                       'password': password
            }
            r = session.post(self.api_protocol
                             + '://'
                             + self.api_host
                             + '/login', data=payload)
    
            if r.status_code == requests.codes.ok:
    
                cookies = session.cookies.get_dict()
                log.debug('Cookies are: %s' %(cookies))
                try:
                    self.write_cookie(cookies)
                    return cookies
                except Exception, e:
                    log.error('Exception: %s' % e)
    
            else:
                log.error('Authentication failed')
                sys.exit(1)
    
        except Exception, e:
            log.error('Exception: %s' % e)
            log.error('Authentication failed')
            sys.exit(1)
    
    
    def check_response_codes(self, r):
        """Checks the response codes and logs appropriate messaging for
           the client"""
    
        if r.status_code == requests.codes.ok:
            log.info('Command successful.')
            return r.json()
        elif r.status_code == requests.codes.conflict:
            log.info('Resource already exists.')
        elif r.status_code == requests.codes.forbidden:
            log.info('Authorization failed.')
        else:
            log.info('Command failed.')
            sys.exit(1)


    def api_submit(self, request, data=None, method='get'):
        """Manages http requests to the API."""
    
        headers = {'content-type': 'application/json'}
    
        api_url = (self.api_protocol
                   + '://'
                   + self.api_host
                   + request)
    
        if method == 'put':
    
            data = json.dumps(data, default=lambda o: o.__dict__)
            cookies = self.get_cookie_auth()
    
            log.debug('Submitting data to API: %s' % api_url)
    
            r = session.put(api_url, verify=self.verify_ssl, cookies=cookies, headers=headers, data=data)
    
            # re-auth if our cookie is invalid/expired
            if r.status_code == requests.codes.unauthorized:
                cookies = self.authenticate()
                r = session.put(api_url, verify=self.verify_ssl, cookies=cookies, headers=headers, data=data)
    
            return self.check_response_codes(r)
    
        elif method == 'delete':
    
            data = json.dumps(data, default=lambda o: o.__dict__)
            cookies = self.get_cookie_auth()
    
            log.debug('Deleting data from API: %s' % api_url)
    
            r = session.delete(api_url, verify=self.verify_ssl, cookies=cookies, headers=headers, data=data)
    
            # re-auth if our cookie is invalid/expired
            if r.status_code == requests.codes.unauthorized:
                cookies = self.authenticate()
                r = session.delete(api_url, verify=self.verify_ssl, cookies=cookies)
    
            return self.check_response_codes(r)
    
        elif method == 'get_params':
            r = session.get(api_url, verify=self.verify_ssl, params=data)
            if r.status_code == requests.codes.ok:
                return r.json()
    
        else:
            r = session.get(api_url, verify=self.verify_ssl)
            if r.status_code == requests.codes.ok:
                return r.json()
    
        return None


class Node(ArsenalClient):
    def __init__(self,
                 unique_id = None,
                 node_name = None,
                 puppet_version = None,
                 facter_version = None,
                 uptime = None,
                 ec2 = None,
                 network = None):
#        super(self.__class__, self).__init__()
#        ArsenalClient.__init__(self, 'foobar', 'barfoo')
        self.unique_id = unique_id
        self.node_name = node_name
        self.puppet_version = puppet_version
        self.facter_version = facter_version
        self.hardware_profile = HardwareProfile()
        self.operating_system = OperatingSystem()
        self.uptime = uptime
        self.ec2 = ec2
        self.network = network


    def get_unique_id(self, **facts):
        """Determines the unique_id of a node"""
    
        log.debug('determining unique_id...')
        if facts['kernel'] == 'Linux' or facts['kernel'] == 'FreeBSD':
            if 'ec2_instance_id' in facts:
                unique_id = facts['ec2_instance_id']
                log.debug('unique_id is from ec2_instance_id: {0}'.format(unique_id))
            elif os.path.isfile('/usr/sbin/dmidecode'):
                unique_id = self.get_uuid()
                if unique_id:
                    log.debug('unique_id is from dmidecode: {0}'.format(unique_id))
                else:
                    unique_id = facts['macaddress']
                    log.debug('unique_id is from mac address: {0}'.format(unique_id))
            else:
                unique_id = facts['macaddress']
                log.debug('unique_id is from mac address: {0}'.format(unique_id))
        else:
            unique_id = facts['macaddress']
            log.debug('unique_id is from mac address: {0}'.format(unique_id))
        return unique_id
    
    
    def get_uuid(self):
        """Gets the uuid of a node from dmidecode if available."""
    
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen( ['/usr/sbin/dmidecode', '-s', 'system-uuid'], stdout=subprocess.PIPE, stderr=FNULL )
        p.wait()
        uuid = p.stdout.readlines()
        # FIXME: Need some validation here
        if uuid:
            return uuid[0].rstrip()
        else:
            # Support older versions of dmidecode
            p = subprocess.Popen( ['/usr/sbin/dmidecode', '-t', '1'], stdout=subprocess.PIPE )
            p.wait()
            dmidecode_out = p.stdout.readlines()
            xen_match = "\tUUID: "
            for line in dmidecode_out:
                if re.match(xen_match, line):
                    return line[7:].rstrip()
    
        return None
    
    
    def get_hardware_profile(self, facts):
        """Collets hardware_profile details of a node."""
    
        log.debug('Collecting hardware profile data.')
        hardware_profile = HardwareProfile()
        try:
            hardware_profile.manufacturer = facts['manufacturer']
            hardware_profile.model = facts['productname']
            log.debug('Hardware profile from dmidecode.')
        except KeyError:
            try:
                xen_match = "xen"
                if re.match(xen_match, facts['virtual']) and facts['is_virtual'] == 'true':
                    hardware_profile.manufacturer = 'Citrix'
                    hardware_profile.model = 'Xen Guest'
                    log.debug('Hardware profile is virtual.')
            except KeyError:
                log.error('Unable to determine hardware profile.')
        return hardware_profile


    def get_operating_system(self, facts):
        """Collets operating_system details of a node."""
    
        log.debug('Collecting operating_system data.')
        operating_system = OperatingSystem()
        try:
            operating_system.variant = facts['operatingsystem']
            operating_system.version_number = facts['operatingsystemrelease']
            operating_system.architecture = facts['architecture']
            operating_system.description = facts['lsbdistdescription']
        except KeyError:
            log.error('Unable to determine operating system.')
    
        return operating_system
    
    
    def collect_data(self):
        """Main data collection function use to register a node."""
    
        log.debug('Collecting data for node.')

        facts = facter()
        self.unique_id = self.get_unique_id(**facts)
    
        # EC2 facts
        if 'ec2_instance_id' in facts:
            ec2 = Ec2()
            ec2.ec2_instance_id = facts['ec2_instance_id']
            ec2.ec2_ami_id = facts['ec2_ami_id']
            ec2.ec2_hostname = facts['ec2_hostname']
            ec2.ec2_public_hostname = facts['ec2_public_hostname']
            ec2.ec2_instance_type = facts['ec2_instance_type']
            ec2.ec2_security_groups = facts['ec2_security_groups']
            ec2.ec2_placement_availability_zone = facts['ec2_placement_availability_zone']
            self.ec2 = ec2
    
        # puppet & facter versions
        if 'puppetversion' in facts:
            self.puppet_version = facts['puppetversion']
            self.facter_version = facts['facterversion']
    
        # Report uptime
        self.uptime = facts['uptime']
    
        self.hardware_profile = self.get_hardware_profile(facts)
    
        self.operating_system = self.get_operating_system(facts)
    
    #    data[operating_system[version_number]] = facts['lsbdistrelease']
    
        #
        # Gather software-related information
        #
        # Use our custom fact for aws. Required since hostname -f
        # doens't work on ec2 hosts.
        # FIXME: need regex match
        if 'ct_fqdn' in facts and facts['ct_loc'] == 'aws1':
           self.node_name = facts['ct_fqdn']
        else:
           self.node_name = facts['fqdn']
    

    def register(self):
        """Collect all the data about a node and register
           it with the server"""
    
        self.collect_data()
    
        log.debug('data is: {0}'.format(json.dumps(self, default=lambda o: o.__dict__)))
        self.api_submit('/api/register', self, method='put')


    def search_nodes(self, args):
        """Search for nodes and perform optional assignment
           actions."""
    
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        # FIXME: Ths is going to get ugly real fast
#        actions = ['set_tags', 'set_status', 'set_node_groups', 'del_node_groups']
#        for a in actions:
#            foo = getattr(args, a)()
#            print "FOO IS: ", foo
#            if foo:
#               globals()[foo](args)
        # FIXME: duped code for set and del
        if args.set_tags:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    _manage_tag_assignments(args, results, 'node')
        if args.del_tags:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    _manage_tag_assignments(args, results, 'node', 'delete')
        if args.set_status:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    self._set_status(args, results)
        if args.set_node_groups:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    self._manage_node_group_assignments(args, results)
        if args.del_node_groups:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    self._manage_node_group_assignments(args, results)
        if args.set_hypervisor:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    self._manage_hypervisor_assignments(args, results)
        if args.del_hypervisor:
            results = _search(args)
            if results:
                r_names = []
                for n in results:
                    r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
                if ask_yes_no("We are ready to update the following nodes: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                    self._manage_hypervisor_assignments(args, results)
    
        if not any((args.set_tags,
                    args.del_tags,
                    args.set_status,
                    args.set_node_groups,
                    args.del_node_groups,
                    args.set_hypervisor,
                    args.del_hypervisor)):
    
            results = _search(args)
    
            if results:
                # FIXME: Doesn't work beyond the top level for individual fields
                if args.fields:
                    for r in results:
                        print '- {0}\n'.format(r['node_name'])
#                        print res['status']['status_name']
                        if args.fields == 'all':
                            # FIXME: Is this really the best way?
                            # This produces ugly formatting
                            # print(yaml.safe_dump(r, encoding='utf-8', allow_unicode=True))
                            #print(yaml.dump(r, default_flow_style=False))
                            c = convert(r)
#                            f = (yaml.dump(c, default_flow_style=False, encoding='utf-8', allow_unicode=True, indent=2))
#                            print textwrap.fill(f, initial_indent='', subsequent_indent='    ')
                            print(yaml.dump(c, default_flow_style=False, encoding='utf-8', allow_unicode=True, indent=2))
    
#                            print json.dumps(r, default=lambda o: o.__dict__, sort_keys=True,
#                                             indent=2, separators=(',', ': ')).
    
                            #for f in r.keys():
                            #    if f == 'node_name':
                            #        continue
                            #    print '    {0}: {1}'.format(f, r[f])
                        else:
                            for f in list(args.fields.split(",")):
                                if f == 'node_name':
                                    continue
                                if type(r[f]) is types.ListType:
                                    print '{0}: \n{1}'.format(f, yaml.safe_dump(r[f], encoding='utf-8', allow_unicode=True))
                                else:
                                    print '    {0}: {1}'.format(f, r[f])
                # Default to returning just the node name
                else:
                    for r in results:
                        print r['node_name']


    def _set_status(self, args, nodes):
        """Set the status of one or more nodes."""
    
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        data = {'status_name': args.set_status}
        status = self.api_submit('/api/statuses', data, method='get_params')
    
        data = {'status_id': status['status_id']}
    
        for n in nodes:
            log.info('Setting status node={0},status={1}'.format(n['node_name'], status['status_name']))
            self.api_submit('/api/nodes/{0}'.format(n['node_id']), data, method='put')
    
    
    def _manage_node_group_assignments(self, args, nodes):
        """Assign or De-assign node_groups to one or more nodes."""
    
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        if args.del_node_groups:
            node_groups_list = args.del_node_groups
            api_action = 'delete'
            log_action = 'Deleting'
        else:
            node_groups_list = args.set_node_groups
            api_action = 'put'
            log_action = 'Assigning'
    
        node_groups = []
        for ng in node_groups_list.split(','):
            data = {'node_group_name': ng}
            r = self.api_submit('/api/node_groups', data, method='get_params')
            if r:
                node_groups.append(r[0])
    
        for n in nodes:
            for ng in node_groups:
                log.info('{0} node_group={1} to node={2}'.format(log_action, ng['node_group_name'], n['node_name']))
                data = {'node_id': n['node_id'],
                        'node_group_id': ng['node_group_id']}
                self.api_submit('/api/node_group_assignments', data, method=api_action)
    
    
    def _manage_hypervisor_assignments(self, args, nodes):
        """Assign or De-assign a hypervisor to one or more nodes."""
    
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        if args.del_hypervisor:
            hypervisor = args.del_hypervisor
            api_action = 'delete'
            log_action = 'Deleting'
        else:
            hypervisor = args.set_hypervisor
            api_action = 'put'
            log_action = 'Assigning'
    
        data = {'unique_id': hypervisor}
        r = self.api_submit('/api/nodes', data, method='get_params')
        if r:
            hypervisor = r['results'][0]
    
        for n in nodes:
            log.info('{0} hypervisor={1},node={2}'.format(log_action, hypervisor['node_name'], n['node_name']))
            data = {'parent_node_id': hypervisor['node_id'],
                    'child_node_id': n['node_id']}
            self.api_submit('/api/hypervisor_vm_assignments', data, method=api_action)


    def create_nodes(self, args):
        """Create a new node."""
    
        # FIXME: Support hardware_profile, and operating_system?
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        # Check if the node exists (by checking unique_id) first
        # so it can ask if you want to update the existing entry, which
        # essentially would just be changing either the node_name or status_id.
        # FIXME: do we want exact_get to be optional on delete? i.e. put it in argparse?
        data = { 'unique_id': args.unique_id,
                 'exact_get': True, }
        r = self.api_submit('/api/nodes', data, method='get_params')
    
        data = {'node_name': args.node_name,
                'unique_id': args.unique_id,
                'node_status_id': args.status_id,
               }
    
        if r:
            if ask_yes_no('Entry already exists: {0}: {1}\n Would you like to update it?'.format(r[0]['node_name'], r[0]['unique_id']), args.answer_yes):
                log.info('Updating node node_name={0},unique_id={1},status_id={2}'.format(args.node_name, args.unique_id, args.status_id))
                self.api_submit('/api/{0}'.format(args.object_type), data, method='put')
    
        else:
            log.info('Creating node node_name={0},unique_id={1},status_id={2}'.format(args.node_name, args.unique_id, args.status_id))
            self.api_submit('/api/{0}'.format(args.object_type), data, method='put')
    
    
    def delete_nodes(self, args):
        """Delete an existing node."""
    
        log.debug('action_command is: {0}'.format(args.action_command))
        log.debug('object_type is: {0}'.format(args.object_type))
    
        if args.node_id:
            # FIXME: do we want exact_get to be optional on delete? i.e. put it in argparse?
            args.exact_get = True
            api_endpoint = '/api/nodes/{0}'.format(args.node_id)
            r = self.api_submit(api_endpoint, method='get')
            # FIXME: individual records don't return a list. Is that ok, or should the api always return a list?
            if r:
                results = [r]
            else:
                results = None
        else:
    
            search = ''
            if args.node_name:
                search = 'node_name={0},'.format(args.node_name)
            if args.unique_id:
                search = 'unique_id={0},'.format(args.unique_id)
    
            args.search = search.rstrip(',')
    
            # FIXME: do we want exact_get to be optional on delete? i.e. put it in argparse?
            args.exact_get = True
            results = _search(args)
    
        if results:
            r_names = []
            for n in results:
                r_names.append('{0}: {1}'.format(n['node_name'], n['unique_id']))
    
            if ask_yes_no("We are ready to delete the following {0}: \n{1}\n Continue?".format(args.object_type, "\n".join(r_names)), args.answer_yes):
                for n in results:
                    log.info('Deleting node_name={0},unique_id={1}'.format(n['node_name'], n['unique_id']))
                    data = {'node_id': n['node_id']}
                    api_submit('/api/{0}/{1}'.format(args.object_type, n['node_id']), data, method='delete')


class Ec2(object):
    def __init__(self, 
                 ec2_instance_id = None,
                 ec2_ami_id = None,
                 ec2_hostname = None,
                 ec2_public_hostname = None,
                 ec2_instance_type = None,
                 ec2_security_groups = None,
                 ec2_placement_availability_zone = None):
        self.ec2_instance_id = ec2_instance_id
        self.ec2_ami_id = ec2_ami_id
        self.ec2_hostname = ec2_hostname
        self.ec2_public_hostname = ec2_public_hostname
        self.ec2_instance_type = ec2_instance_type
        self.ec2_security_groups = ec2_security_groups
        self.ec2_placement_availability_zone = ec2_placement_availability_zone
 

class HardwareProfile(object):
    def __init__(self,
                 manufacturer = 'Unknown',
                 model = 'Unknown'):
        self.manufacturer = manufacturer
        self.model = model


class OperatingSystem(object):
    def __init__(self,
                 variant = 'Unknown',
                 version_number = 'Unknown',
                 architecture = 'Unknown',
                 description = 'Unknown'):
        self.variant = variant
        self.version_number = version_number
        self.architecture = architecture
        self.description = description


class NodeGroup(object):
    def __init__(self,
                 node_group_name = None,
                 node_group_owner = None,
                 description = None):
        self.node_group_name = node_group_name
        self.node_group_owner = node_group_owner
        self.description = description


def facter():
    """Reads in facts from facter"""

    # need this for custom facts - can add additional paths if needed
    os.environ["FACTERLIB"] = "/var/lib/puppet/lib/facter"
    p = subprocess.Popen( ['facter'], stdout=subprocess.PIPE )
    p.wait()
    lines = p.stdout.readlines()
    lines = dict(k.split(' => ') for k in
                   [s.strip() for s in lines if ' => ' in s])
    
    return lines


def _search(args):
    """Main serach function to query the API."""

    log.debug('Searching for {0}'.format(args.object_type))
    log.debug('action_command is: {0}'.format(args.action_command))

    search_terms = list(args.search.split(","))
    data = dict(u.split("=") for u in search_terms)
    data['exact_get'] = args.exact_get
    log.debug('data is: {0}'.format(data))

    api_endpoint = '/api/{0}'.format(args.object_type)
    results = api_submit(api_endpoint, data, method='get_params')

    # The client doesn't need metadata
    if not results['results']:
        log.info('No results found for search.')
        return None
    else:
        r = results['results']
        return r


def gen_help(help_type):
    """Generte the list of searchable terms for help"""

    terms = {
        'nodes_search': [ 'node_id', 'node_name', 'unique_id', 'status_id',
                          'status', 'hardware_profile_id', 'hardware_profile',
                          'operating_system_id', 'operating_system', 'uptime',
                          'node_groups', 'created', 'updated', 'updated_by',
        ],
        'node_groups_search': [ 'node_group_id', 'node_group_name',
                                'node_group_owner', 'description',
        ],
        'tags_search': [ 'tag_id', 'tag_name', 'tag_value',
        ],
        'hypervisor_vm_assignments_search': [ 'parent_id', 'child_id',
        ],
    }

    return '[ {0} ]'.format(', '.join(sorted(terms[help_type])))


def ask_yes_no(question, answer_yes=None, default='no'):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """

    if answer_yes:
        return True

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


## NODES

def convert(data):
    """Helper method to format output. (might not be final solution)"""

    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data




## NODE_GROUPS
def search_node_groups(args):
    """Search for node groups and perform optional assignment
       actions."""

    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    if (args.set_tags or args.del_tags):
        results = _search(args)
        if results:
            r_names = []
            for ng in results:
                r_names.append('node_group_name={0},node_group_id={1}'.format(ng['node_group_name'], ng['node_group_id']))
            if ask_yes_no("We are ready to update the following node_groups: \n{0}\n Continue?".format("\n".join(r_names)), args.answer_yes):
                api_action = 'set'
                if args.del_tags:
                    api_action = 'delete'
                _manage_tag_assignments(args, results, 'node_group', api_action)
 
    if not any((args.set_tags, args.del_tags)):

        results = _search(args)

        if results:
            if args.fields:
                for r in results:
                    print '- {0}'.format(r['node_group_name'])
                    #FIXME: gross output, duplicate code
                    if args.fields == 'all':
                        for f in r.keys():
                            if f == 'node_group_name':
                                continue
                            if type(r[f]) is types.ListType:
                                print '{0}: \n{1}'.format(f, yaml.safe_dump(r[f], encoding='utf-8', allow_unicode=True))
                            else:
                                print '    {0}: {1}'.format(f, r[f])
                    else:
                        for f in list(args.fields.split(",")):
                            if f == 'node_group_name':
                                continue
                            if type(r[f]) is types.ListType:
                                print '{0}: \n{1}'.format(f, yaml.safe_dump(r[f], encoding='utf-8', allow_unicode=True))
                            else:
                                print '    {0}: {1}'.format(f, r[f])

            # Default to returning just the node_group name
            else:
                for r in results:
                    print r['node_group_name']


def create_node_groups(args):
    """Create a new node_group."""

    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    data = {'node_group_name': args.node_group_name,
            'node_group_owner': args.node_group_owner,
            'node_group_description': args.node_group_description,
           }

    log.info('Creating node_group node_group_name={0},node_group_owner={1},node_group_description={2}'.format(args.node_group_name, args.node_group_owner, args.node_group_description))
    api_submit('/api/{0}'.format(args.object_type), data, method='put')


def delete_node_groups(args):
    """Delete an existing node_group."""

    # FIXME: Support name and id or ?
    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    args.search = 'node_group_name={0}'.format(args.node_group_name)
    # FIXME: do we want exact_get to be optional on delete? i.e. put it in argparse?
    args.exact_get = True
    results = _search(args)

    if results:
        r_names = []
        for n in results:
            r_names.append(n['node_group_name'])

        if ask_yes_no("We are ready to delete the following {0}: \n{1}\n Continue?".format(args.object_type, "\n".join(r_names)), args.answer_yes):
            for n in results:
                log.info('Deleting node_group_name={0}'.format(n['node_group_name']))
                data = {'node_group_id': n['node_group_id']}
                # FIXME: name? id? both?
                api_submit('/api/{0}/{1}'.format(args.object_type, n['node_group_id']), data, method='delete')


## TAGS
def search_tags(args):
    """Search for tags and perform optional assignment
       actions."""

    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    if args.set_tags:
        set_tag(args)

    # switch to any if there's more than one
    if not args.set_tags:

        results = _search(args)

        if args.fields:
            for r in results:
                print '- {0}'.format(r['tag_name'])
                if args.fields == 'all':
                    for f in r.keys():
                        if f == 'tag_name':
                            continue
                        print '    {0}: {1}'.format(f, r[f])
                else:
                    for f in list(args.fields.split(",")):
                        if f == 'tag_name':
                            continue
                        print '    {0}: {1}'.format(f, r[f])
        # Default to returning just the tag name
        else:
            for r in results:
                print r['tag_name']


def _manage_tag_assignments(args, objects, action_object, api_action = 'set'):
    """Assign or De-assign tags to one or more objects (nodes or node_groups)."""

    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    o_id = action_object + '_id'
    o_name = action_object + '_name'
    # FIXME: clunky
    if api_action == 'delete':
        my_tags = args.del_tags
        http_method = 'delete'
    else:
        my_tags = args.set_tags
        http_method = 'put'

    tags = []
    for t in my_tags.split(','):
        lst = t.split('=')
        data = {'tag_name': lst[0],
                'tag_value': lst[1]
        }
        r = api_submit('/api/tags', data, method='get_params')
        if r:
            tags.append(r[0])
        else:
            log.info('tag not found, creating')
            r = api_submit('/api/tags', data, method='put')
            tags.append(r)

    for o in objects:
        for t in tags:
            log.info('{0} tag {1}={2} to {3}={4}'.format(api_action, t['tag_name'], t['tag_value'], o_name, o[o_name]))
            data = {o_id: o[o_id],
                    'tag_id': t['tag_id']}
            api_submit('/api/tag_{0}_assignments'.format(action_object), data, method=http_method)


def create_tags(args):
    """Create a new tag."""

    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    data = {'tag_name': args.tag_name,
            'tag_value': args.tag_value,
           }

    log.info('Creating tag tag_name={0},tag_value={1}'.format(args.tag_name, args.tag_value))
    api_submit('/api/{0}'.format(args.object_type), data, method='put')


def delete_tags(args):
    """Delete an existing tag."""

    # FIXME: Support name and id or ?
    log.debug('action_command is: {0}'.format(args.action_command))
    log.debug('object_type is: {0}'.format(args.object_type))

    args.search = 'tag_name={0},tag_value={1}'.format(args.tag_name, args.tag_value)
    # FIXME: do we want exact_get to be optional on delete? i.e. put it in argparse?
    args.exact_get = True
    results = _search(args)

    if results:
        r_names = []
        for n in results:
            r_names.append('{0}={1}'.format(n['tag_name'], n['tag_value']))

        if ask_yes_no("We are ready to delete the following {0}: \n{1}\n Continue?".format(args.object_type, "\n".join(r_names)), args.answer_yes):
            for n in results:
                log.info('Deleting tag_name={0},tag_value={1}'.format(n['tag_name'], n['tag_value']))
                data = {'tag_id': n['tag_id']}
                # FIXME: name? id? both?
                api_submit('/api/{0}/{1}'.format(args.object_type, n['tag_id']), data, method='delete')


def check_root(login):
    """Check and see if we're running as root"""
    if not os.geteuid() == 0:
        log.error('Login {0} must run as root.'.format(login))
        sys.exit(1)

