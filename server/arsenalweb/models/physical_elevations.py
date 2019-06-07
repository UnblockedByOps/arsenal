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
    Integer,
    TIMESTAMP,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
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
    id = Column(Integer, primary_key=True, nullable=False)
    elevation = Column(Text, nullable=False)
    physical_rack_id = Column(Integer, ForeignKey('physical_racks.id'), nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    physical_rack = relationship('PhysicalRack', backref='physical_elevations', lazy='joined')

    def __json__(self, request):
        try:
            # FIXME: Not sure if this constraint is going to cause
            # other problems.
            if request.path_info.startswith('/api/physical_elevations'):
                fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    elevation=self.elevation,
                    physical_rack=get_name_id_dict([self.physical_rack]),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
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

            return resp


class PhysicalElevationAudit(BaseAudit):
    '''Arsenal PhysicalElevationAudit object.'''

    __tablename__ = 'physical_elevations_audit'
