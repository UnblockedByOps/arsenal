'''Arsenal client Nodes class.'''
import os
import re
import subprocess
import logging
from arsenalclient.authorization import check_root
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.arsenal_facts import ArsenalFacts


LOG = logging.getLogger(__name__)

class Nodes(ArsenalInterface):
    '''The arsenal client Nodes class.'''

    def __init__(self, **kwargs):
        super(Nodes, self).__init__(**kwargs)
        self.uri = '/api/nodes'
        self.arsenal_facts = ArsenalFacts()

    # Overridden methods
    def search(self, params=None):
        '''Search for nodes.

        Usage:

        >>> params = {
        ...   'name': 'fopp-cbl.*(inf1|lab1)',
        ...   'status': 'inservice',
        ... }
        >>> Nodes.search(params)

        Args:
            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Nodes, self).search(params=params)

    def create(self, params):
        '''Create a node.

        Args:
            params (dict): A dictionary of url parameters for the request. The
                following keys are required:
                    unique_id
                    name
                    status_id

        Usage:

        >>> params = {
        ...     'unique_id': 'abc123',
        ...     'name': 'hostname1.example.com',
        ...     'status_id': 2,
        ...     'operating_system': {
        ...         'id': 1,
        ...     },
        ...     'hardware_profile': {
        ...         'id': 1,
        ...     },
        ... }
        >>> Nodes.create(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Nodes, self).create(params)

    def update(self, params):
        '''Update a node.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only the params in the example are updatable from this action.

        >>> params = {
        ...     'unique_id': 'abc123',
        ...     'name': 'hostname1.example.com',
        ...     'status_id': 4,
        ...     'operating_system': {
        ...         'id': 1,
        ...     },
        ...     'hardware_profile': {
        ...         'id': 1,
        ...     },
        ... }
        >>> Nodes.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Nodes, self).update(params)

    def delete(self, params):
        '''Delete a node object from the server.

        Args:

            params: A node dictionary to delete. Must contain the
                node id, unique_id, and name.

        Usage:

        >>> params = {
        ...     'id': 56,
        ...     'unique_id': 'abc123',
        ...     'name': 'hostname1.example.com',
        ... }
        >>> Nodes.delete(params)
        '''

        LOG.info('Deleting node name: {0} unique_id: {1}'.format(params['name'],
                                                                 params['unique_id']))
        return super(Nodes, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for nodes.'''
        return super(Nodes, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single node by it's name.

        Args:
            name (str): A string representing the node name you wish to find.
        '''
        return super(Nodes, self).get_by_name(name)

    # Custom methods
    def register(self):
        '''Collect all the data about a node and register it with the server. '''

        LOG.debug('Triggering node registration...')

        if check_root():
            LOG.debug('Overriding login for node registration to: kaboom')
            self.authorization.user_login = 'kaboom'
            my_cookie = '/root/.{0}_kaboom_cookie'.format(self.settings.api_host)
            LOG.debug('Overriding setting for user kaboom: '
                      'cookie_file={0}'.format(my_cookie))
            self.authorization.cookie_file = my_cookie
            node = self.collect()

            LOG.info('Registering node name: {0} unique_id: {1}'.format(node['name'],
                                                                        node['unique_id']))
            resp = self.api_conn('/api/register', node, method='put')

            return resp

    def collect(self):
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
        unique_id = self.get_unique_id()
        resp['unique_id'] = unique_id

        resp['hardware_profile'] = self.get_hardware_profile()

        resp['operating_system'] = self.get_operating_system()

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

    def get_hardware_profile(self):
        '''Collect all the information about the node's hardware_profile. Required
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

    def get_operating_system(self):
        '''Collect all the information about the node's operating_system. Required
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

    @staticmethod
    def get_uuid_from_dmidecode():
        '''Gets the uuid of a node from dmidecode if available. Returns a
        string if found, None otherwise. Also skips known bad output from
        dmidecode that is not unique.'''

        bogus_uuids = [
            '03000200-0400-0500-0006-000700080009',
            'Not Settable',
        ]

        unique_id = None
        file_null = open(os.devnull, 'w')
        proc = subprocess.Popen(['/usr/sbin/dmidecode', '-s', 'system-uuid'],
                                stdout=subprocess.PIPE,
                                stderr=file_null)
        proc.wait()
        uuid = proc.stdout.readlines()
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

    def get_unique_id(self):
        '''Determines the unique_id of a node and returns it as a string.'''

        if not check_root():
            return None

        LOG.debug('Determining unique_id...')
        facts = self.arsenal_facts.facts

        unique_id = facts['networking']['mac_address']

        if facts['os']['kernel'] == 'Linux' or facts['os']['kernel'] == 'FreeBSD':

            if facts['ec2']['instance_id']:
                unique_id = facts['ec2']['instance_id']
                LOG.debug('unique_id is from ec2 instance_id: {0}'.format(unique_id))
            elif facts['hardware']['name'] == 'Red Hat KVM':
                LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
            elif os.path.isfile('/usr/sbin/dmidecode'):
                unique_id = self.get_uuid_from_dmidecode()
                if unique_id:
                    LOG.debug('unique_id is from dmidecode: {0}'.format(unique_id))
                else:
                    unique_id = facts['networking']['mac_address']
                    LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
            else:
                LOG.debug('unique_id is from mac address: {0}'.format(unique_id))
        else:
            LOG.debug('unique_id is from mac address: {0}'.format(unique_id))

        return unique_id

    def enc(self, name, param_sources=None):
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

        resp = self.api_conn('/api/enc', data, log_success=False)

        return resp
