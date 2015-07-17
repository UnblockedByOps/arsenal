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
import arrow
from dateutil import tz
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def _localize_date(obj):
        utc = arrow.get(obj)
        zone = 'US/Pacific' # FIXME: This needs to be configurable somehow
        return  utc.to(tz.gettz(zone)).format('YYYY-MM-DD HH:mm:ss ZZ')


class Node(Base):
    __tablename__ = 'nodes'
    node_id                  = Column(Integer, primary_key=True, nullable=False)
    name                     = Column(Text, nullable=False)
    unique_id                = Column(Text, nullable=False)
    status_id                = Column(Integer, ForeignKey('statuses.status_id'), nullable=False)
    hardware_profile_id      = Column(Integer, ForeignKey('hardware_profiles.hardware_profile_id'), nullable=False)
    uptime                   = Column(Text, nullable=False)
    created                  = Column(TIMESTAMP, nullable=False)
    updated                  = Column(TIMESTAMP, nullable=False)
    updated_by               = Column(Text, nullable=False)
    status                   = relationship("Status", backref=backref('nodes'))

    def __json__(self, request):
        return dict(
            node_id=self.node_id,
            name=self.name,
            unique_id=self.unique_id,
            status_id=self.status_id,
            hardware_profile_id=self.hardware_profile_id,
            status=self.status,
            uptime=self.uptime,
            created=self.created.isoformat(),
            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )

    # FIXME: Not working
    def __xml__(self, request):
        return dict(
            node_id=self.node_id,
            name=self.name,
            unique_id=self.unique_id,
            uptime=self.uptime,
            created=self.created.isoformat(),
            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )


class Status(Base):
    __tablename__ = 'statuses'
    status_id        = Column(Integer, primary_key=True, nullable=False)
    name             = Column(Text, nullable=False)
    description      = Column(Text, nullable=False)
    created          = Column(TIMESTAMP, nullable=False)
    updated          = Column(TIMESTAMP, nullable=False)
    updated_by       = Column(Text, nullable=False)

    def __json__(self, request):
        return dict(
            status_id=self.status_id,
            name=self.name,
            description=self.description,
            created=self.created.isoformat(),
            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )


class User(Base):
    __tablename__ = 'users'
    user_id          = Column(Integer, primary_key=True, nullable=False)
    user_name        = Column(Text, nullable=False) # email address
    first_name       = Column(Text, nullable=True)
    last_name        = Column(Text, nullable=True)
    salt             = Column(Text, nullable=False)
    password         = Column(Text, nullable=False)
    updated_by       = Column(Text, nullable=False)
    created          = Column(TIMESTAMP, nullable=False)
    updated          = Column(TIMESTAMP, nullable=False)

    @hybrid_method
    def get_all_assignments(self):
        ga = []
        for a in self.local_user_group_assignments:
            ga.append(a.group.group_name)
        return ga

    @hybrid_property
    def localize_date_created(self):
        local = _localize_date(self.created)
        return local

    @hybrid_property
    def localize_date_updated(self):
        local = _localize_date(self.updated)
        return local


class LocalUserGroupAssignment(Base):
    __tablename__ = 'local_user_group_assignments'
    user_group_assignment_id = Column(Integer, primary_key=True, nullable=False)
    group_id                = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    user_id                 = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    updated_by              = Column(Text, nullable=False)
    created                 = Column(TIMESTAMP, nullable=False)
    updated                 = Column(TIMESTAMP, nullable=False)
    user                    = relationship("User", backref=backref('local_user_group_assignments'))
    group                   = relationship("Group", backref=backref('local_user_group_assignments'))


class Group(Base):
    __tablename__ = 'groups'
    group_id         = Column(Integer, primary_key=True, nullable=False)
    group_name       = Column(Text, nullable=False)
    updated_by       = Column(Text, nullable=False)
    created          = Column(TIMESTAMP, nullable=False)
    updated          = Column(TIMESTAMP, nullable=False)

    @hybrid_method
    def get_all_assignments(self):
        ga = []
        for a in self.group_perm_assignments:
            ga.append(a.group_perms.perm_name)
        return ga

    @hybrid_property
    def localize_date_created(self):
        local = _localize_date(self.created)
        return local

    @hybrid_property
    def localize_date_updated(self):
        local = _localize_date(self.updated)
        return local

class GroupPermAssignment(Base):
    __tablename__ = 'group_perm_assignments'
    group_assignment_id     = Column(Integer, primary_key=True, nullable=False)
    group_id                = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    perm_id                 = Column(Integer, ForeignKey('group_perms.perm_id'), nullable=False)
    updated_by              = Column(Text, nullable=False)
    created                 = Column(TIMESTAMP, nullable=False)
    updated                 = Column(TIMESTAMP, nullable=False)
    group                   = relationship("Group", backref=backref('group_perm_assignments'))

    @hybrid_method
    def get_assignments_by_group(self, group_name):
        q = DBSession.query(GroupPermAssignment)
        q = q.join(Group, GroupPermAssignment.group_id == Group.group_id)
        q = q.filter(Group.group_name==group_name)
        return q.all()

    @hybrid_method
    def get_assignments_by_perm(self, perm_name):
        q = DBSession.query(GroupPermAssignment)
        q = q.join(Group, GroupPermAssignment.group_id == Group.group_id)
        q = q.join(GroupPerm, GroupPermAssignment.perm_id == GroupPerm.perm_id)
        q = q.filter(GroupPerm.perm_name==perm_name)
        return q.all()


class GroupPerm(Base):
    __tablename__ = 'group_perms'
    perm_id                = Column(Integer, primary_key=True, nullable=False)
    perm_name              = Column(Text, nullable=False)
    created                = Column(TIMESTAMP, nullable=False)
    group_perm_assignments = relationship("GroupPermAssignment", backref=backref('group_perms'),
                                          order_by=GroupPermAssignment.created.desc,
                                          lazy="dynamic")

    def __repr__(self):
        return "GroupPerm(perm_id='%s', perm_name='%s', )" % (
                      self.perm_id, self.perm_name)

    @hybrid_method
    def get_all_assignments(self):
        ga = []
        for a in self.group_perm_assignments:
            ga.append(a.group.group_name)
        return ga

    @hybrid_method
    def get_group_perm_id(self, perm_name):
        # Convert the perm name to the id
        q = DBSession.query(GroupPerm)
        q = q.filter(GroupPerm.perm_name == '%s' % perm_name)
        return q.one()


