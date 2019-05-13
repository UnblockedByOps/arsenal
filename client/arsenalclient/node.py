'''Arsenal client Node object'''
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
from __future__ import print_function
import os
import subprocess
import re
import logging

from arsenalclient.version import __version__

from arsenalclient.hardware_profile import HardwareProfile
from arsenalclient.operating_system import OperatingSystem
from arsenalclient.network_interface import NetworkInterface
from arsenalclient.ec2 import Ec2

LOG = logging.getLogger(__name__)


class Node(object):
    '''Node object

    Args:
        api_conn: An api connection object from Client.
        unique_id: A string representing the unique_id of the node (required).
        name: A string representing the name of the node (required).
        status_id: An int representing the status_id to set for the node (required).
        hardware_profile: An arsenalclient.hardware_profile.HardwareProfile object.
        operating_system: An arsenalclient.operating_system.OperatingSystem object.
        ec2: An arsenalclient.ec2.Ec2 object.
        network_interfaces: A list of arsenalclient.network_interface.NetworkInterface
            objects.
    '''

    def __init__(self,
                 api_conn,
                 **kwargs):

        self.api_conn = api_conn
        self.id = None
        self.unique_id = None
        self.name = None
        self.status_id = None
        self.hardware_profile = HardwareProfile(self.api_conn, id=1)
        self.operating_system = OperatingSystem(self.api_conn, id=1)
        self.ec2 = None
        self.guest_vms = None
        self.network_interfaces = None
        self.uptime = None
        self.serial_number = None
        self.processor_count = None

        self.__dict__.update((key, val) for key, val in kwargs.iteritems() if
                             key in
                             self.__dict__)

        if not self.network_interfaces:
            self.network_interfaces = []
        if not self.guest_vms:
            self.guest_vms = []

    def get_unique_id(self, facts):
        ''' Determines the unique_id of a node. '''

        LOG.debug('determining unique_id...')

        if facts['os']['kernel'] == 'Linux' or facts['os']['kernel'] == 'FreeBSD':
            if facts['virtual'] == 'kvm':
                self.unique_id = facts['networking']['mac_address']
                LOG.debug('unique_id is from mac address: {0}'.format(self.unique_id))
            elif facts['ec2']['instance_id']:
                self.unique_id = facts['ec2']['instance_id']
                LOG.debug('unique_id is from ec2 instance_id: {0}'.format(self.unique_id))
            elif os.path.isfile('/usr/sbin/dmidecode'):
                self.get_uuid()
                if self.unique_id:
                    LOG.debug('unique_id is from dmidecode: {0}'.format(self.unique_id))
                else:
                    self.unique_id = facts['networking']['mac_address']
                    LOG.debug('unique_id is from mac address: {0}'.format(self.unique_id))
            else:
                self.unique_id = facts['networking']['mac_address']
                LOG.debug('unique_id is from mac address: {0}'.format(self.unique_id))
        else:
            self.unique_id = facts['networking']['mac_address']
            LOG.debug('unique_id is from mac address: {0}'.format(self.unique_id))

    def get_uuid(self):
        ''' Gets the uuid of a node from dmidecode (if available). '''

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
        # TODO: Need some validation here
        if uuid:
            strip_uuid = uuid[-1].rstrip()
            if strip_uuid in bogus_uuids:
                LOG.warn('unique_id from dmidecode is known bad: {0}'.format(strip_uuid))
            else:
                self.unique_id = strip_uuid
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
                        self.unique_id = strip_uuid

    def collect(self, facts):
        '''Collect all data about a node. '''

        LOG.debug('Collecting data for node.')

        self.get_unique_id(facts)
        self.name = facts['networking']['fqdn']

        self.hardware_profile = HardwareProfile(self.api_conn)
        self.hardware_profile.collect(facts)

        self.operating_system = OperatingSystem(self.api_conn)
        self.operating_system.collect(facts)

        if facts['ec2']['instance_id']:
            LOG.debug('Ec2 data collection not yet implemented.')

        self.uptime = facts['uptime']

        if facts['hardware']['serial_number']:
            self.serial_number = facts['hardware']['serial_number']
        if facts['processors']['count']:
            self.processor_count = facts['processors']['count']

        for net_if in facts['networking']['interfaces']:
            my_attribs = facts['networking']['interfaces'][net_if]
            # Use the node's unqiue_id prefixed with the interface name if it
            # doesn't have a mac addres (sit, veth, etc.).
            if not 'unique_id' in my_attribs:
                unique_id = '{0}_{1}'.format(net_if, self.unique_id)
                my_attribs['unique_id'] = unique_id
            # Bonded interfaces inherit the mac address of whatever interface is
            # currently primary, therefore we cannot use mac as a bond's unique_id.
            # Instead we use the node's unqiue_id prefixed with the interface name.
            if net_if.startswith('bond') or net_if.startswith('br'):
                unique_id = '{0}_{1}'.format(net_if, self.unique_id)
                my_attribs['unique_id'] = unique_id
            # Set the bond IP on it's slaves too.
            else:
                my_master = my_attribs.get('bond_master')
                if my_master:
                    try:
                        my_ip = facts['networking']['interfaces'][my_master]['ip_address']
                        my_attribs['ip_address'] = my_ip
                    except KeyError:
                        pass
            self.network_interfaces.append(NetworkInterface(name=net_if,
                                                            **my_attribs))

        if facts['guest_vms']:
            self.guest_vms = facts['guest_vms']

    def submit(self, uri='/api/nodes'):
        '''Submit a node object to the server and define the node id.'''

        resp = self.api_conn(uri, self, method='put')
        try:
            self.id = resp['id']
        except KeyError:
            pass

    def delete(self):
        '''Delete a node object from the server'''

        LOG.info('Deleting node '
                 'name={0},unique_id={1}'.format(self.name,
                                                 self.unique_id))

        self.api_conn('/api/nodes/{0}'.format(self.id), method='delete')
