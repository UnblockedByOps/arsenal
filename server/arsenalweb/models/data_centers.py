'''Arsenal data_centers DB Model'''
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
    Text,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class DataCenter(Base):
    '''Arsenal DataCenter object.'''

    __tablename__ = 'data_centers'
    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    status_id = Column(INTEGER(unsigned=True), ForeignKey('statuses.id'), nullable=False)
    status = relationship('Status', backref='data_centers', lazy='joined')
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    updated_by = Column(VARCHAR(200), nullable=False)
    tags = relationship('Tag',
                        secondary='tag_data_center_assignments',
                        backref='data_centers',
                        lazy='dynamic')


    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    status=get_name_id_dict([self.status]),
                    tags=get_name_id_list(self.tags, extra_keys=['value']),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
                # Always return name and id, then return whatever additional fields
                # are asked for.
                resp = get_name_id_dict([self])

                my_fields = fields.split(',')

                # Backrefs are not in the instance dict, so we handle them here.
                if 'tags' in my_fields:
                    resp['tags'] = get_name_id_list(self.tags,
                                                    extra_keys=['value'])

                resp.update((key, getattr(self, key)) for key in my_fields if
                            key in self.__dict__)

                return jsonify(resp)

        # Default to returning only name and id.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp

Index('idx_data_center_id', DataCenter.id, unique=False)
Index('idx_unique_data_center_name', DataCenter.name, unique=True)



class DataCenterAudit(BaseAudit):
    '''Arsenal DataCenterAudit object.'''

    __tablename__ = 'data_centers_audit'
