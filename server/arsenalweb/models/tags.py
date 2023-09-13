'''Arsenal tags DB Model'''
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
    Index,
    TIMESTAMP,
    UniqueConstraint,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class Tag(Base):
    '''Arsenal Tag object.'''

    __tablename__ = 'tags'
    __table_args__ = (
        UniqueConstraint('name', 'value', name='idx_uniq_tag'),
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    value = Column(VARCHAR(255), nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)


    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                try:
                    self.value = int(self.value)
                except ValueError:
                    pass

                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    value=self.value,
                    nodes=get_name_id_list(self.nodes),
                    node_groups=get_name_id_list(self.node_groups),
                    data_centers=get_name_id_list(self.data_centers),
                    physical_devices=get_name_id_list(self.physical_devices,
                                                      default_keys=
                                                      ['id', 'serial_number']),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return id, name, and value, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self], extra_keys=['value'])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'nodes' in my_fields:
                resp['nodes'] = get_name_id_list(self.nodes)
            if 'node_groups' in my_fields:
                resp['node_groups'] = get_name_id_list(self.node_groups)
            if 'data_centers' in my_fields:
                resp['data_centers'] = get_name_id_list(self.data_centers)
            if 'physical_devices' in my_fields:
                resp['physical_devices'] = get_name_id_list(self.physical_devices)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)
            try:
                resp['value'] = int(resp['value'])
            except ValueError:
                pass

            return jsonify(resp)

        # Default to returning only id, value, and name.
        except KeyError:
            resp = get_name_id_dict([self], extra_keys=['value'])

            return resp

Index('idx_tag_id', Tag.id, unique=False)

class TagAudit(BaseAudit):
    '''Arsenal TagAudit object.'''

    __tablename__ = 'tags_audit'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )
