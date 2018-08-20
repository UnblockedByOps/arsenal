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
    Integer,
    TIMESTAMP,
    Text,
)
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
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)


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
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
                # Always return id, name, and value, then return whatever additional fields
                # are asked for.
                resp = get_name_id_dict([self], extra_keys=['value'])

                my_fields = fields.split(',')

                # Backrefs are not in the instance dict, so we handle them here.
                if 'nodes' in my_fields:
                    resp['nodes'] = get_name_id_list(self.nodes)
                if 'node_groups' in my_fields:
                    resp['node_groups'] = get_name_id_list(self.node_groups)

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


class TagAudit(BaseAudit):
    '''Arsenal TagAudit object.'''

    __tablename__ = 'tags_audit'
