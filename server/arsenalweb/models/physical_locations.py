'''Arsenal physical_locations DB Model'''
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


class PhysicalLocation(Base):
    '''Arsenal PhysicalLocation object.'''

    __tablename__ = 'physical_locations'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    provider = Column(Text, nullable=True)
    address_1 = Column(Text, nullable=True)
    address_2 = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    admin_area = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    postal_code = Column(Text, nullable=True)
    contact_name = Column(Text, nullable=True)
    phone_number = Column(Text, nullable=True)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    def __json__(self, request):
        try:
            if request.path_info.startswith('/api/physical_locations'):
                fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    provider=self.provider,
                    address_1=self.address_1,
                    address_2=self.address_2,
                    city=self.city,
                    admin_area=self.admin_area,
                    country=self.country,
                    postal_code=self.postal_code,
                    contact_name=self.contact_name,
                    phone_number=self.phone_number,
                    physcial_racks=get_name_id_list(self.physical_racks,
                                                    default_keys=['id',
                                                                  'name',
                                                                  'physical_elevations']),
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


class PhysicalLocationAudit(BaseAudit):
    '''Arsenal PhysicalLocationAudit object.'''

    __tablename__ = 'physical_locations_audit'
