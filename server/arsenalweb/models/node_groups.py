'''Arsenal node_groups DB Model'''
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
from sqlalchemy.orm import relationship
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class NodeGroup(Base):
    '''Arsenal NodeGroup object.'''

    __tablename__ = 'node_groups'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    owner = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=False)
    notes_url = Column(Text, nullable=True)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    updated_by = Column(VARCHAR(200), nullable=False)
    tags = relationship('Tag',
                        secondary='tag_node_group_assignments',
                        backref='node_groups',
                        lazy='dynamic')


    @hybrid_method
    def find_node_group_by_name(self, name):
        '''Find a node_group by name.'''

        query = DBSession.query(NodeGroup)
        query = query.filter(NodeGroup.name == '%s' % name)

        return query.one()

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    owner=self.owner,
                    description=self.description,
                    notes_url=self.notes_url,
                    tags=get_name_id_list(self.tags, extra_keys=['value']),
                    nodes=get_name_id_list(self.nodes),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return name and id, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'nodes' in my_fields:
                resp['nodes'] = get_name_id_list(self.nodes)
            if 'tags' in my_fields:
                resp['tags'] = get_name_id_list(self.tags,
                                                extra_keys=['value'])

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only name, id, and unique_id.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


Index('idx_node_group_id', NodeGroup.id, unique=False)
Index('idx_unique_node_group_name', NodeGroup.name, unique=True)


class NodeGroupAudit(BaseAudit):
    '''Arsenal NodeGroupAudit object.'''

    __tablename__ = 'node_groups_audit'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )
