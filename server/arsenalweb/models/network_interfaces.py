'''Arsenal network_interfaces DB Model'''
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


class NetworkInterface(Base):
    '''Arsenal NetworkInterface object.'''

    __tablename__ = 'network_interfaces'
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
    unique_id = Column(VARCHAR(255), nullable=False)
    ip_address_id = Column(INTEGER(unsigned=True), ForeignKey('ip_addresses.id'),
                           nullable=True)
    ip_address = relationship('IpAddress', backref='network_interfaces',
                              lazy='joined')
    bond_master = Column(Text, nullable=True)
    port_description = Column(Text, nullable=True)
    port_number = Column(Text, nullable=True)
    port_switch = Column(Text, nullable=True)
    port_vlan = Column(Text, nullable=True)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)


    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    unique_id=self.unique_id,
                    ip_address=get_name_id_dict([self.ip_address],
                                                default_keys=['id', 'ip_address']),
                    bond_master=self.bond_master,
                    port_description=self.port_description,
                    port_number=self.port_number,
                    port_switch=self.port_switch,
                    port_vlan=self.port_vlan,
                    nodes=get_name_id_list(self.nodes),
                    created=self.created,
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return name, id, and unique_id, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self], extra_keys=['unique_id'])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'nodes' in my_fields:
                resp['nodes'] = get_name_id_list(self.nodes)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only name, id, and unique_id.
        except KeyError:
            resp = get_name_id_dict([self], extra_keys=['unique_id'])

            return resp


Index('idx_network_interface_id', NetworkInterface.id, unique=False)
Index('idx_unique_network_interface_unique_id', NetworkInterface.unique_id, unique=True)


class NetworkInterfaceAudit(BaseAudit):
    '''Arsenal NetworkInterfaceAudit object.'''

    __tablename__ = 'network_interfaces_audit'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )
