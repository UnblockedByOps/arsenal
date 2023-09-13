'''Arsenal physical_elevations DB Model'''
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
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    jsonify,
)

LOG = logging.getLogger(__name__)


class PhysicalElevation(Base):
    '''Arsenal PhysicalElevation object.'''

    __tablename__ = 'physical_elevations'
    __table_args__ = (
        UniqueConstraint('elevation',
                         'physical_rack_id',
                         name='idx_physical_elevation_location'),
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    elevation = Column(VARCHAR(11), nullable=False)
    physical_rack_id = Column(INTEGER(unsigned=True),
                              ForeignKey('physical_racks.id'),
                              nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)

    physical_rack = relationship('PhysicalRack', backref='physical_elevations', lazy='joined')
    physical_device = relationship('PhysicalDevice',
                                   primaryjoin='PhysicalElevation.id==PhysicalDevice.physical_elevation_id',
                                   backref='physical_elevation')

    def __json__(self, request):
        try:
            if request.path_info.startswith('/api/physical_elevations'):
                fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    elevation=self.elevation,
                    physical_device=get_name_id_dict(self.physical_device,
                                                     default_keys=['id',
                                                                   'serial_number',
                                                                   'hardware_profile']),
                    physical_rack=get_name_id_dict([self.physical_rack],
                                                   default_keys=['id',
                                                                 'name',
                                                                 'physical_location']),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return id and name, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only these fields.
        except (KeyError, UnboundLocalError):
            resp = get_name_id_dict([self], default_keys=['id',
                                                          'elevation',])
            resp['physical_device'] = get_name_id_dict(self.physical_device,
                                                       default_keys=['id',
                                                                     'serial_number',
                                                                     'hardware_profile'])


            return resp


Index('idx_physical_elevation_id', PhysicalElevation.id, unique=True)


class PhysicalElevationAudit(BaseAudit):
    '''Arsenal PhysicalElevationAudit object.'''

    __tablename__ = 'physical_elevations_audit'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )
