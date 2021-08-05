'''Arsenal physical_devices DB Model'''
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
    TIMESTAMP,
    UniqueConstraint,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    check_null_string,
    get_name_id_dict,
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class PhysicalDevice(Base):
    '''Arsenal PhysicalDevice object.'''

    __tablename__ = 'physical_devices'
    __table_args__ = (
        UniqueConstraint('physical_rack_id',
                         'physical_elevation_id',
                         name='idx_physical_device_rack_elevation'),
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    serial_number = Column(VARCHAR(255), nullable=False)
    physical_location_id = Column(INTEGER(unsigned=True),
                                  ForeignKey('physical_locations.id'),
                                  nullable=False)
    physical_location = relationship('PhysicalLocation',
                                     backref='physical_devices',
                                     lazy='joined')
    physical_rack_id = Column(INTEGER(unsigned=True),
                              ForeignKey('physical_racks.id'),
                              nullable=False)
    physical_rack = relationship('PhysicalRack',
                                 backref='physical_devices',
                                 lazy='joined')
    physical_elevation_id = Column(INTEGER(unsigned=True),
                                   ForeignKey('physical_elevations.id'),
                                   nullable=False)
    status_id = Column(INTEGER(unsigned=True), ForeignKey('statuses.id'), nullable=False)
    status = relationship('Status', backref='physical_devices', lazy='joined')
    mac_address_1 = Column(VARCHAR(255), nullable=False)
    mac_address_2 = Column(VARCHAR(255), nullable=True)
    hardware_profile_id = Column(INTEGER(unsigned=True),
                                 ForeignKey('hardware_profiles.id'),
                                 nullable=False)
    hardware_profile = relationship('HardwareProfile',
                                    backref=backref('physical_devices'),
                                    lazy='joined')
    oob_ip_address = Column(VARCHAR(255), nullable=True)
    oob_mac_address = Column(VARCHAR(255), nullable=True)
    tags = relationship('Tag',
                        secondary='tag_physical_device_assignments',
                        backref='physical_devices',
                        lazy='dynamic')

    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)


    def __json__(self, request):
        try:
            if request.path_info.startswith('/api/physical_devices'):
                fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    id=self.id,
                    hardware_profile=get_name_id_dict([self.hardware_profile],
                                                      default_keys=['id',
                                                                    'name',
                                                                    'rack_u',
                                                                    'rack_color']),
                    physical_location=self.physical_location,
                    physical_rack=self.physical_rack,
                    physical_elevation=self.physical_elevation,
                    status=get_name_id_dict([self.status]),
                    mac_address_1=self.mac_address_1,
                    mac_address_2=self.mac_address_2,
                    node=get_name_id_dict(self.nodes),
                    oob_ip_address=self.oob_ip_address,
                    oob_mac_address=self.oob_mac_address,
                    serial_number=check_null_string(self.serial_number),
                    tags=get_name_id_list(self.tags, extra_keys=['value']),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return these fields, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self], default_keys=['id',
                                                          'serial_number',
                                                         ])

            my_fields = fields.split(',')

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            if 'node' in my_fields:
                resp['node'] = get_name_id_dict(self.nodes)
            if 'tags' in my_fields:
                resp['tags'] = get_name_id_list(self.tags,
                                                extra_keys=['value'])

            return jsonify(resp)

        # Default to returning only these fields.
        except (KeyError, UnboundLocalError):
            resp = get_name_id_dict([self], default_keys=['id',
                                                          'serial_number',
                                                         ])

            return resp


Index('idx_physical_device_id', PhysicalDevice.id, unique=False)
Index('idx_physical_device_serial_number', PhysicalDevice.serial_number, unique=True)


class PhysicalDeviceAudit(BaseAudit):
    '''Arsenal PhysicalDeviceAudit object.'''

    __tablename__ = 'physical_devices_audit'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )
