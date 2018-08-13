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
    Integer,
    TIMESTAMP,
    Text,
)
from arsenalweb.models.common import (
    Base,
    BaseAudit,
    DBSession,
    jsonify,
    localize_date,
)

LOG = logging.getLogger(__name__)


class Ec2(Base):
    '''Arsenal Ec2 object.'''

    __tablename__ = 'ec2'
    id = Column(Integer, primary_key=True, nullable=False)
    instance_id = Column(Text, nullable=False)
    ami_id = Column(Text, nullable=False)
    hostname = Column(Text, nullable=False)
    public_hostname = Column(Text, nullable=False)
    instance_type = Column(Text, nullable=False)
    security_groups = Column(Text, nullable=False)
    placement_availability_zone = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    def __json__(self, request):
        return dict(
            id=self.id,
            instance_id=self.instance_id,
            ami_id=self.ami_id,
            hostname=self.hostname,
            public_hostname=self.public_hostname,
            instance_type=self.instance_type,
            security_groups=self.security_groups,
            placement_availability_zone=self.placement_availability_zone,
            created=localize_date(self.created),
            updated=localize_date(self.updated),
            updated_by=self.updated_by,
            )
