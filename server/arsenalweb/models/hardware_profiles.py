'''Arsenal hardware_profiles DB Model'''
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
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    Text,
)
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    DBSession,
    get_name_id_dict,
    jsonify,
    localize_date,
)

LOG = logging.getLogger(__name__)


class HardwareProfile(Base):
    '''Arsenal HardwareProfile object.'''

    __tablename__ = 'hardware_profiles'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    manufacturer = Column(Text, nullable=False)
    rack_u = Column(Integer, nullable=False)
    rack_color = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    @hybrid_method
    def get_hardware_profile_id(self, manufacturer, model):
        '''Find a hardware_profile id by name.'''

        query = DBSession.query(HardwareProfile)
        query = query.filter(HardwareProfile.manufacturer == '%s' % manufacturer)
        query = query.filter(HardwareProfile.model == '%s' % model)
        try:
            hw_profile = query.one()
            return hw_profile.id
        except:
            return None

    def __json__(self, request):
        try:
            if request.path_info.startswith('/api/hardware_profiles'):
                fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    model=self.model,
                    manufacturer=self.manufacturer,
                    rack_u=self.rack_u,
                    rack_color=self.rack_color,
                    created=localize_date(self.created),
                    updated=localize_date(self.updated),
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
                # Always return name and id, then return whatever additional fields
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


class HardwareProfileAudit(BaseAudit):
    '''Arsenal HardwareProfileAudit object.'''

    __tablename__ = 'hardware_profiles_audit'
