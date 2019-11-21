'''Arsenal physical_racks DB Model'''
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
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class PhysicalRack(Base):
    '''Arsenal PhysicalRack object.'''

    __tablename__ = 'physical_racks'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    physical_location_id = Column(Integer, ForeignKey('physical_locations.id'), nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    physical_location = relationship('PhysicalLocation', backref='physical_racks', lazy='joined')

    def __json__(self, request):
        try:
            if request.path_info.startswith('/api/physical_racks'):
                fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    physical_location=get_name_id_dict([self.physical_location]),
                    physical_elevations=self.physical_elevations,
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

        # Default to returning only name and id.
        except (KeyError, UnboundLocalError):
            resp = get_name_id_dict([self])

            return resp


class PhysicalRackAudit(BaseAudit):
    '''Arsenal PhysicalRackAudit object.'''

    __tablename__ = 'physical_racks_audit'
