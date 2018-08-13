'''Arsenal operating_systems DB Model'''
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
)

LOG = logging.getLogger(__name__)


class OperatingSystem(Base):
    '''Arsenal OperatingSystem object.'''

    __tablename__ = 'operating_systems'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    variant = Column(Text, nullable=False)
    version_number = Column(Text, nullable=False)
    architecture = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    @hybrid_method
    def get_operating_system_id(self, variant, version_number, architecture):
        '''Get operating_system id by name.'''

        query = DBSession.query(OperatingSystem)
        query = query.filter(OperatingSystem.variant == '%s' % variant)
        query = query.filter(OperatingSystem.version_number == '%s' % version_number)
        query = query.filter(OperatingSystem.architecture == '%s' % architecture)
        return query.one()

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    variant=self.variant,
                    version_number=self.version_number,
                    architecture=self.architecture,
                    description=self.description,
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

        # Default to returning only id and name.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


class OperatingSystemAudit(BaseAudit):
    '''Arsenal OperatingSystemAudit object.'''

    __tablename__ = 'operating_systems_audit'
