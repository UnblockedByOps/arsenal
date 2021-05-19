'''Arsenal statuses DB Model'''
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
    Index,
    TIMESTAMP,
    Text,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    jsonify,
)

LOG = logging.getLogger(__name__)


class Status(Base):
    '''Arsenal Status object.'''

    __tablename__ = 'statuses'
    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    updated_by = Column(VARCHAR(200), nullable=False)

    @hybrid_method
    def get_status_id(self, name):
        '''Find a status id by name.'''

        query = DBSession.query(Status)
        query = query.filter(Status.name == name)
        try:
            status = query.one()
            return status.id
        except:
            return None

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    description=self.description,
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return name and id, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')
            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only name and id.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


Index('idx_status_name_id', Status.id, unique=False)
Index('idx_status_name_uniq', Status.name, unique=True)


class StatusAudit(BaseAudit):
    '''Arsenal StatusAudit object.'''

    __tablename__ = 'statuses_audit'
