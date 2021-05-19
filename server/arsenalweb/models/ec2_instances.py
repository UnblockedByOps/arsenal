'''Arsenal EC2 DB Model'''
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
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    get_name_id_dict,
    jsonify,
    localize_date,
)

LOG = logging.getLogger(__name__)


class Ec2Instance(Base):
    '''Arsenal Ec2Instance object.'''

    __tablename__ = 'ec2_instances'
    id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    account_id = Column(VARCHAR(255), nullable=False)
    ami_id = Column(VARCHAR(255), nullable=False)
    hostname = Column(VARCHAR(255), nullable=False)
    instance_id = Column(VARCHAR(255), nullable=False)
    instance_type = Column(VARCHAR(255), nullable=False)
    availability_zone = Column(VARCHAR(255), nullable=False)
    profile = Column(VARCHAR(255), nullable=False)
    reservation_id = Column(VARCHAR(255), nullable=False)
    security_groups = Column(VARCHAR(255), nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    updated_by = Column(VARCHAR(200), nullable=False)

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':
                # Everything.
                all_fields = dict(
                    id=self.id,
                    account_id=self.account_id,
                    ami_id=self.ami_id,
                    hostname=self.hostname,
                    instance_id=self.instance_id,
                    instance_type=self.instance_type,
                    availability_zone=self.availability_zone,
                    profile=self.profile,
                    reservation_id=self.reservation_id,
                    security_groups=self.security_groups,
                    created=localize_date(self.created),
                    updated=localize_date(self.updated),
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return id and instance_id, then return whatever additional fields
            # are asked for.
            resp = get_name_id_dict([self], default_keys=['id', 'instance_id'])

            my_fields = fields.split(',')
            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only instance_id and id.
        except KeyError:
            resp = get_name_id_dict([self], default_keys=['id', 'instance_id'])

            return resp


Index('idx_ec2_id', Ec2Instance.id, unique=False)
Index('idx_ec2_instance_id', Ec2Instance.instance_id, unique=True)


class Ec2InstanceAudit(BaseAudit):
    '''Arsenal Ec2InstanceAudit object.'''

    __tablename__ = 'ec2_instances_audit'
