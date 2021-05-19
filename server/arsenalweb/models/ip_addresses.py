'''Arsenal ip_addresses DB Model'''
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
    text,
)
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    get_name_id_list,
    jsonify,
)

LOG = logging.getLogger(__name__)


class IpAddress(Base):
    '''Arsenal IpAddress object.'''

    __tablename__ = 'ip_addresses'
    id = Column(Integer, primary_key=True, nullable=False)
    ip_address = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    updated_by = Column(Text, nullable=False)

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    ip_address=self.ip_address,
                    network_interfaces=get_name_id_list(self.network_interfaces),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            else:
                # Always return ip_address and id, then return whatever additional fields
                # are asked for.
                resp = get_name_id_dict([self], default_keys=['id', 'ip_address'])

                my_fields = fields.split(',')
                resp.update((key, getattr(self, key)) for key in my_fields if
                            key in self.__dict__)

                # Backrefs are not in the instance dict, so we handle them here.
                if 'network_interfaces' in my_fields:
                    resp['network_interfaces'] = get_name_id_list(self.network_interfaces)

                return jsonify(resp)

        # Default to returning only ip_address and id.
        except KeyError:
            resp = get_name_id_dict([self], default_keys=['id', 'ip_address'])

            return resp


class IpAddressAudit(BaseAudit):
    '''Arsenal IpAddressAudit object.'''

    __tablename__ = 'ip_addresses_audit'
