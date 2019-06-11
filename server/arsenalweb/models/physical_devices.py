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
    Integer,
    TIMESTAMP,
    Text,
)
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
    id = Column(Integer, primary_key=True, nullable=False)
    serial_number = Column(Text, nullable=False)
    physical_location_id = Column(Integer,
                                  ForeignKey('physical_locations.id'),
                                  nullable=False)
    physical_location = relationship('PhysicalLocation',
                                     backref='physical_devices',
                                     lazy='joined')
    physical_rack_id = Column(Integer,
                              ForeignKey('physical_racks.id'),
                              nullable=False)
    physical_rack = relationship('PhysicalRack',
                                 backref='physical_devices',
                                 lazy='joined')
    physical_elevation_id = Column(Integer,
                                   ForeignKey('physical_elevations.id'),
                                   nullable=False)
    physical_elevation = relationship('PhysicalElevation',
                                      backref='physical_devices',
                                      lazy='joined')
    hardware_profile_id = Column(Integer,
                                 ForeignKey('hardware_profiles.id'),
                                 nullable=True)
    hardware_profile = relationship('HardwareProfile',
                                    backref=backref('physical_devices'),
                                    lazy='joined')
    oob_ip_address = Column(Text, nullable=True)
    oob_mac_address = Column(Text, nullable=True)

    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)


    def __json__(self, request):
        try:
            # FIXME: Not sure if this constraint is going to cause
            # other problems.
            if request.path_info.startswith('/api/physical_devices'):
                fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    id=self.id,
                    physical_location=self.physical_location,
                    physical_rack=self.physical_rack,
                    physical_elevation=self.physical_elevation,
                    hardware_profile=get_name_id_dict([self.hardware_profile]),
                    node=get_name_id_dict(self.nodes),
                    oob_ip_address=self.oob_ip_address,
                    oob_mac_address=self.oob_mac_address,
                    serial_number=check_null_string(self.serial_number),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
                # Always return these fields, then return whatever additional fields
                # are asked for.
                resp = get_name_id_dict([self], default_keys=['id',
                                                              'serial_number',
                                                              'oob_ip_address',
                                                              'oob_mac_address',
                                                              'physical_location',
                                                              'physical_rack',
                                                              'physical_elevation',
                                                             ])

                my_fields = fields.split(',')

                resp.update((key, getattr(self, key)) for key in my_fields if
                            key in self.__dict__)

                if 'node' in my_fields:
                    resp['node'] = get_name_id_dict(self.nodes)

                return jsonify(resp)

        # Default to returning only these fields.
        except (KeyError, UnboundLocalError):
            resp = get_name_id_dict([self], default_keys=['id',
                                                          'serial_number',
                                                          'oob_ip_address',
                                                          'oob_mac_address',
                                                          'physical_location',
                                                          'physical_rack',
                                                          'physical_elevation',
                                                         ])

            return resp


class PhysicalDeviceAudit(BaseAudit):
    '''Arsenal PhysicalDeviceAudit object.'''

    __tablename__ = 'physical_devices_audit'
