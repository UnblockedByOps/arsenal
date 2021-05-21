'''Arsenal nodes DB Model'''
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
import logging
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    TIMESTAMP,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    check_null_dict,
    check_null_string,
    get_name_id_dict,
    get_name_id_list,
    hypervisor_vm_assignments,
    jsonify,
)

LOG = logging.getLogger(__name__)


class Node(Base):
    '''Arsenal Node object.'''

    __tablename__ = 'nodes'
    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    unique_id = Column(VARCHAR(255), nullable=False)
    status_id = Column(INTEGER(unsigned=True), ForeignKey('statuses.id'), nullable=False)
    hardware_profile_id = Column(INTEGER(unsigned=True),
                                 ForeignKey('hardware_profiles.id'),
                                 nullable=False)
    operating_system_id = Column(INTEGER(unsigned=True),
                                 ForeignKey('operating_systems.id'),
                                 nullable=False)
    ec2_id = Column(INTEGER(unsigned=True), ForeignKey('ec2_instances.id'))
    data_center_id = Column(INTEGER(unsigned=True), ForeignKey('data_centers.id'))
    uptime = Column(VARCHAR(255))
    #serial_number = Column(VARCHAR(255), ForeignKey('physical_devices.serial_number'))
    serial_number = Column(VARCHAR(255))
    os_memory = Column(VARCHAR(255))
    processor_count = Column(Integer)
    last_registered = Column(TIMESTAMP)
    created = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    updated_by = Column(VARCHAR(200), nullable=False)
    status = relationship('Status', backref='nodes', lazy='joined')
    hardware_profile = relationship('HardwareProfile', backref=backref('nodes'), lazy='joined')
    operating_system = relationship('OperatingSystem', backref=backref('nodes'), lazy='joined')
    ec2_instance = relationship('Ec2Instance', backref=backref('nodes'), lazy='joined')
    data_center = relationship('DataCenter', backref=backref('nodes'), lazy='joined')
    physical_device = relationship('PhysicalDevice',
                                   backref=backref('nodes'),
                                   lazy='joined',
                                   primaryjoin='Node.serial_number==PhysicalDevice.serial_number',
                                   foreign_keys=[serial_number])
    node_groups = relationship('NodeGroup',
                               secondary='node_group_assignments',
                               backref='nodes',
                               lazy='dynamic')
    tags = relationship('Tag',
                        secondary='tag_node_assignments',
                        backref='nodes',
                        lazy='dynamic')
    network_interfaces = relationship('NetworkInterface',
                                      secondary='network_interface_assignments',
                                      backref='nodes',
                                      lazy='dynamic')
    hypervisor = relationship('Node',
                              secondary='hypervisor_vm_assignments',
                              primaryjoin=hypervisor_vm_assignments.c.guest_vm_id == id,
                              secondaryjoin=hypervisor_vm_assignments.c.hypervisor_id == id,
                              backref='guest_vms',
                              lazy='dynamic')

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    unique_id=self.unique_id,
                    status=get_name_id_dict([self.status]),
                    hardware_profile=get_name_id_dict([self.hardware_profile]),
                    operating_system=get_name_id_dict([self.operating_system]),
                    ec2_instance=check_null_dict(self.ec2_instance),
                    data_center=get_name_id_dict([self.data_center]),
                    uptime=check_null_string(self.uptime),
                    serial_number=check_null_string(self.serial_number),
                    os_memory=check_null_string(self.os_memory),
                    processor_count=check_null_string(self.processor_count),
                    node_groups=get_name_id_list(self.node_groups),
                    tags=get_name_id_list(self.tags, extra_keys=['value']),
                    network_interfaces=get_name_id_list(self.network_interfaces,
                                                        extra_keys=[
                                                            'unique_id',
                                                        ]),
                    guest_vms=get_name_id_list(self.guest_vms),
                    hypervisor=get_name_id_list(self.hypervisor),
                    physical_device=self.physical_device,
                    last_registered=self.last_registered,
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return name id and unique_id, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self], extra_keys=['unique_id'])

            my_fields = fields.split(',')

            # Dynamic backrefs are not in the instance dict, so we handle them here.
            if 'node_groups' in my_fields:
                resp['node_groups'] = get_name_id_list(self.node_groups)
            if 'hypervisor' in my_fields:
                resp['hypervisor'] = get_name_id_list(self.hypervisor)
            if 'guest_vms' in my_fields:
                my_guest_vms = get_name_id_list(self.guest_vms)
                if my_guest_vms:
                    resp['guest_vms'] = my_guest_vms
                # Need this so we don't return an empty list of guest_vms
                # for each guest vm.
                else:
                    del resp['guest_vms']
            if 'tags' in my_fields:
                resp['tags'] = get_name_id_list(self.tags,
                                                extra_keys=['value'])
            if 'network_interfaces' in my_fields:
                resp['network_interfaces'] = get_name_id_list(self.network_interfaces,
                                                              extra_keys=[
                                                                  'unique_id',
                                                                  'ip_address',
                                                                  'bond_master',
                                                                  'port_description',
                                                                  'port_number',
                                                                  'port_switch',
                                                                  'port_vlan',
                                                              ])

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            # These are in the dict because it is joined, but we
            # want to add extra fields.
            if 'physical_device' in my_fields and self.physical_device:
                resp['physical_device'] = get_name_id_dict([self.physical_device],
                                                           default_keys=[
                                                               'id',
                                                               'serial_number',
                                                           ],
                                                           extra_keys=[
                                                               'physical_location',
                                                               'physical_rack',
                                                               'physical_elevation',
                                                           ])

            if 'ec2_instance' in my_fields and self.ec2_id:
                resp['ec2_instance'] = get_name_id_dict([self.ec2_instance],
                                                        default_keys=[
                                                            'id',
                                                            'instance_id',
                                                        ],
                                                        extra_keys=[
                                                            'account_id',
                                                            'ami_id',
                                                            'hostname',
                                                            'instance_type',
                                                            'availability_zone',
                                                            'profile',
                                                            'reservation_id',
                                                            'security_groups',
                                                        ])

            return jsonify(resp)

        # Default to returning only name, id, and unique_id.
        except KeyError:
            resp = get_name_id_dict([self], extra_keys=['unique_id'])

            return resp


Index('idx_node_id', Node.id, unique=False)
Index('idx_node_name', Node.name, unique=False)
Index('idx_node_serial_number', Node.serial_number, unique=False)
Index('idx_node_ec2_id', Node.ec2_id, unique=True)


class NodeAudit(BaseAudit):
    '''Arsenal NodeAudit object.'''

    __tablename__ = 'nodes_audit'
