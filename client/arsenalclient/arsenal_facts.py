'''Arsenal facts class'''
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
import logging
import subprocess
import ast
import json
import re
try:
    import libvirt

    def libvirt_callback(ignore, err):
        '''Callback function to suppress libvirt warnings.'''

        if err[3] != libvirt.VIR_ERR_ERROR:
            # Don't log libvirt errors: global error handler will do that
            logging.warn('Non-error from libvirt: {0}'.format(err[2]))
    libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)

except ImportError:
    pass

LOG = logging.getLogger(__name__)


class ArsenalFacts(object):
    '''The Arsenal Facts class.

    Usage::

      >>> from arsenalclient.arsenal_facts import ArsenalFacts
      >>> my_facts = ArsenalFacts()
      >>> my_facts.resolve()
      >>> print my_facts.facts['uptime']
      20:43 hours
    '''

    def __init__(self):

        self.facts = {
            'uptime': None,
            'data_center': {
                'name': None,
            },
            'ec2': {
                'account_id': None,
                'ami_id': None,
                'availability_zone': None,
                'hostname': None,
                'instance_id': None,
                'instance_type': None,
                'profile': None,
                'reservation_id': None,
                'security_groups': None,
            },
            'hardware': {
                'manufacturer': None,
                'product_name': None,
                'name': None,
                'virtual': None,
                'is_virtual': None,
                'serial_number': 'Unknown',
            },
            'networking': {
                'fqdn': None,
                'mac_address': None,
                'interfaces': {},
            },
            'os': {
                'name': None,
                'variant': None,
                'version_number': None,
                'architecture': None,
                'description': None,
                'kernel': None,
            },
            'processors': {
                'count': None,
            },
            'memory': {
                'system': {
                    'total': None,
                }
            },
            'guest_vms': [],
        }
        self.facts_resolved = False

    def resolve(self, provider='_facter'):
        '''Resolve all Arsenal facts to their final values. Allows for swapping out
        facter for another fact collector of your choosing. Each fact collector must
        provide values for all of the facts defined in __init__ in order to
        function correctly.'''

        if not self.facts_resolved:
            getattr(self, provider)()
            LOG.debug(json.dumps(self.facts, indent=2, sort_keys=True))
            LOG.debug('Setting facts_resolved = True.')
            self.facts_resolved = True
        else:
            LOG.debug('Facts already resolved, skipping resolution.')

    def _facter(self):
        '''Reads in facts from facter and stores them in a dict.'''

        LOG.debug('Gathering facts...')
        if os.path.isfile('/opt/puppetlabs/bin/facter'):
            facter_bin = '/opt/puppetlabs/bin/facter'
            facter_style = 'modern'
        else:
            facter_bin = 'facter'
            facter_style = 'legacy'

        LOG.debug('Using {0} facts...'.format(facter_style))

        facter_cmd = [
            facter_bin,
            '-p',
            '--json',
        ]

        try:
            proc = subprocess.Popen(
                facter_cmd,
                stdin=open(os.devnull),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(None)
            resp = json.loads(stdout)
        except:
            LOG.error('Unable to collect facts! Error: {0}'.format(stderr))
            raise

        if facter_style == 'modern':
            self._map_facter_modern(resp)
        else:
            self._map_facter_legacy(resp)

        LOG.debug('Gathering facts complete.')

    def _map_facter_modern(self, resp):
        '''Map modern facter facts to arsenal facts for later use in the client
        code.'''

        LOG.debug('Mapping modern facts...')
        self.facts['uptime'] = resp['system_uptime']['uptime']
        try:
            self.facts['hardware']['manufacturer'] = resp['dmi']['manufacturer']
            self.facts['hardware']['product_name'] = resp['dmi']['product']['name']
            hw_name = '{0} {1}'.format(resp['dmi']['manufacturer'],
                                       resp['dmi']['product']['name'])
            self.facts['hardware']['name'] = hw_name
            LOG.debug('Hardware profile from dmidecode.')
        except KeyError:
            try:
                xen_match = "xen"
                if re.match(xen_match, resp['virtual']) and resp['is_virtual']:
                    self.facts['hardware']['manufacturer'] = 'Citrix'
                    self.facts['hardware']['product_name'] = 'Xen Guest'
                    self.facts['hardware']['name'] = 'Citrix Xen Guest'
                    LOG.debug('Hardware profile is virtual.')
            except KeyError:
                LOG.error('Unable to determine hardware profile.')
        self.facts['hardware']['virtual'] = resp['virtual']
        self.facts['hardware']['is_virtual'] = resp['is_virtual']
        try:
            self.facts['hardware']['serial_number'] = resp['dmi']['product']['serial_number']
        except KeyError:
            LOG.warn('Unable to determine serial number.')
        self.facts['networking']['fqdn'] = resp['networking']['fqdn']
        self.facts['networking']['mac_address'] = resp['networking']['mac']
        try:
            os_name = '{0} {1} {2}'.format(resp['os']['name'],
                                           resp['os']['distro']['release']['full'],
                                           resp['os']['architecture'])
            self.facts['os']['name'] = os_name
            self.facts['os']['variant'] = resp['os']['name']
            self.facts['os']['version_number'] = resp['os']['distro']['release']['full']
            self.facts['os']['architecture'] = resp['os']['architecture']
            self.facts['os']['description'] = resp['os']['distro']['description']
            self.facts['os']['kernel'] = resp['kernel']
        except KeyError:
            LOG.error('Unable to determine operating system.')
        self.facts['memory']['system']['total'] = resp['memory']['system']['total']
        self.facts['processors']['count'] = resp['processors']['count']
        try:
            self.facts['ec2']['ami_id'] = resp['ec2_metadata']['ami-id']
            self.facts['ec2']['availability_zone'] = resp['ec2_metadata']['placement']['availability-zone']
            self.facts['ec2']['hostname'] = resp['ec2_metadata']['hostname']
            self.facts['ec2']['instance_id'] = resp['ec2_metadata']['instance-id']
            self.facts['ec2']['instance_type'] = resp['ec2_metadata']['instance-type']
            self.facts['ec2']['profile'] = resp['ec2_metadata']['profile']
            self.facts['ec2']['reservation_id'] = resp['ec2_metadata']['reservation-id']
            self.facts['ec2']['security_groups'] = resp['ec2_metadata']['security-groups'].replace('\n', ',')

            # The value of this fact is a dictionary in string format for some
            # reason.
            account_string = resp['ec2_metadata']['identity-credentials']['ec2']['info']
            account_dict = ast.literal_eval(account_string)
            self.facts['ec2']['account_id'] = account_dict['AccountId']

        except KeyError:
            LOG.debug('ec2 facts not found, nothing to do.')
        self._map_network_interfaces(resp)
        self._map_data_center(resp)
        self._map_guest_vms()

    def _map_guest_vms(self):
        '''If this is a hypervisor, find it's guest vms for inclusion in the
        payload. Sets self.facts['guest_vms'] to a list of dicts, each  with
        the following keys:

        name: The fqdn of the guest vm.
        unique_id: The unique_id of the guest vm.
        '''

        # Potential to add other hypervisor types later.
        if 'libvirt' in sys.modules:
            self._map_libvirt_guests()

    def _map_libvirt_guests(self):
        '''Find guests on a libvirt managed hypervisor.'''

        try:
            try:
                conn = libvirt.open('qemu:///system')
            except libvirt.libvirtError:
                conn = libvirt.open('xen:///system')

            domains = conn.listAllDomains(0)
            if len(domains) != 0:
                for domain in domains:
                    mac_addresses = re.search(r"<mac address='([A-Z0-9:]+)'",
                                              domain.XMLDesc(),
                                              re.IGNORECASE).groups()
                    this_guest = {
                        'name': domain.name(),
                        'unique_id': mac_addresses[0]
                    }
                    self.facts['guest_vms'].append(this_guest)
        except:
            LOG.verbose('Libvirt loaded but unable to connect')

    def _map_network_interfaces(self, resp):
        '''Map network interface information for modern facter facts to arsenal
        facts for later use in the client. We skip loopback (unneccessary) and
        veth (change every time a container is restarted) interfaces from
        collection.'''

        results = {}
        skip_interfaces = (
            'lo',
            'veth',
        )
        for net_if in resp['networking']['interfaces']:
            if net_if.startswith(skip_interfaces):
                LOG.debug('Skipping interface: {0}'.format(net_if))
                continue

            LOG.debug('Network interface found: {0}'.format(net_if))
            results[net_if] = {}
            if 'ip' in resp['networking']['interfaces'][net_if]:
                results[net_if]['ip_address'] = resp['networking']['interfaces'][net_if]['ip']

            try:
                if 'int_switchports' in resp:
                    for key in resp['int_switchports'][net_if]:
                        results[net_if][key] = resp['int_switchports'][net_if][key]
            except KeyError:
                pass

            # Bonded interfaces get their unique_id during the call to register.
            if net_if.startswith('bond'):
                continue
            if 'mac' in resp['networking']['interfaces'][net_if]:
                results[net_if]['unique_id'] = resp['networking']['interfaces'][net_if]['mac']

        self.facts['networking']['interfaces'] = results

    def _map_data_center(self, resp):
        '''Map data_center information for modern facter facts to arsenal
        facts for later use in the client. We are using a custom fact for this.
        In the future we can make alternate implementations configrable here.'''

        try:
            self.facts['data_center']['name'] = resp['int_datacenter']
        except KeyError:
            pass

    def _map_facter_legacy(self, resp):
        '''Map legacy facter facts to arsenal facts for later use in the client
        code.'''

        LOG.debug('Mapping legacy facts...')
        self.facts['uptime'] = resp['uptime']
        try:
            self.facts['hardware']['manufacturer'] = resp['manufacturer']
            self.facts['hardware']['product_name'] = resp['productname']
            hw_name = '{0} {1}'.format(resp['manufacturer'],
                                       resp['productname'])
            self.facts['hardware']['name'] = hw_name
            LOG.debug('Hardware profile from dmidecode.')
        except KeyError:
            try:
                xen_match = "xen"
                if re.match(xen_match, resp['virtual']) and resp['is_virtual']:
                    self.facts['hardware']['manufacturer'] = 'Citrix'
                    self.facts['hardware']['product_name'] = 'Xen Guest'
                    self.facts['hardware']['name'] = 'Citrix Xen Guest'
                    LOG.debug('Hardware profile is virtual.')
            except KeyError:
                LOG.error('Unable to determine hardware profile.')
        self.facts['hardware']['virtual'] = resp['virtual']
        self.facts['hardware']['is_virtual'] = resp['is_virtual']
        try:
            self.facts['hardware']['serial_number'] = resp['serialnumber']
        except KeyError:
            LOG.warn('Unable to determine serial number.')
        self.facts['networking']['fqdn'] = resp['fqdn']
        self.facts['networking']['mac_address'] = resp['macaddress']
        try:
            os_name = '{0} {1} {2}'.format(resp['operatingsystem'],
                                           resp['operatingsystemrelease'],
                                           resp['architecture'])
            self.facts['os']['name'] = os_name
            self.facts['os']['variant'] = resp['operatingsystem']
            self.facts['os']['version_number'] = resp['operatingsystemrelease']
            self.facts['os']['architecture'] = resp['architecture']
            self.facts['os']['description'] = resp['lsbdistdescription']
            self.facts['os']['kernel'] = resp['kernel']
        except KeyError:
            LOG.error('Unable to determine operating system.')
        self.facts['processors']['count'] = resp['processorcount']
        try:
            self.facts['ec2']['instance_id'] = resp['ec2_instance_id']
            self.facts['ec2']['hostname'] = resp['ec2_hostname']
            self.facts['ec2']['ami_id'] = resp['ec2_ami_id']
            self.facts['ec2']['public_hostname'] = resp['ec2_public_hostname']
            self.facts['ec2']['instance_type'] = resp['ec2_instance_type']
            self.facts['ec2']['security_groups'] = resp['ec2_security_groups']
            self.facts['ec2']['availability_zone'] = resp['ec2_placement_availability_zone']
        except KeyError:
            pass
