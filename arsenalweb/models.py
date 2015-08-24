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
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def _localize_date(obj):
    try:
        utc = arrow.get(obj)
        # FIXME: This needs to be configurable somehow
        zone = 'US/Pacific'
        return utc.to(tz.gettz(zone)).format('YYYY-MM-DD HH:mm:ss ZZ')
    except:
        return 'Datetime object'


class Node(Base):
    __tablename__ = 'nodes'
    node_id                  = Column(Integer, primary_key=True, nullable=False)
    node_name                = Column(Text, nullable=False)
    unique_id                = Column(Text, nullable=False)
    status_id                = Column(Integer, ForeignKey('statuses.status_id'), nullable=False)
    hardware_profile_id      = Column(Integer, ForeignKey('hardware_profiles.hardware_profile_id'), nullable=False)
    operating_system_id      = Column(Integer, ForeignKey('operating_systems.operating_system_id'), nullable=False)
    uptime                   = Column(Text, nullable=False)
    created                  = Column(TIMESTAMP, nullable=False)
    updated                  = Column(TIMESTAMP, nullable=False)
    updated_by               = Column(Text, nullable=False)
    status                   = relationship("Status", backref=backref('nodes'))
    hardware_profile         = relationship("HardwareProfile", backref=backref('nodes'))
    operating_system         = relationship("OperatingSystem", backref=backref('nodes'))


    @hybrid_property
    def node_groups(self):
        ngs = []
        for a in self.node_group_assignments:
            # Test to make sure the node group wasn't deleted after the 
            # assignment was made
            if a.node_groups:
                ngs.append(a.node_groups.__json__(self))
        return ngs

    @hybrid_property
    def tags(self):
        tags = []
        for a in self.tag_node_assignments:
            # Test to make sure the node group wasn't deleted after the
            # assignment was made
            if a.tags:
                tags.append(a.tags.__json__(self))
        return tags

    @hybrid_property
    def guest_vms(self):
        guest_vms = []
        try:
            for c in self.hva_parent:
                guest_vms.append({'guest': {'node_id': c.child_node.node_id, 'node_name': c.child_node.node_name}})
        # FIXME: Test if this is still needed
        except NoResultFound:
            pass
        return guest_vms

    @hybrid_property
    def hypervisor(self):
        hypervisor = { }
        try:
            for c in self.hva_child:
                hypervisor = {'node_id': c.parent_node.node_id, 'node_name': c.parent_node.node_name}
        # FIXME: Test if this is still needed
        except AttributeError:
            pass
        except NoResultFound:
            pass
        return hypervisor

    def __json__(self, request):
        return dict(
            node_id=self.node_id,
            node_name=self.node_name,
            unique_id=self.unique_id,
            status_id=self.status_id,
            status=self.status,
            hardware_profile_id=self.hardware_profile_id,
            hardware_profile=self.hardware_profile,
            operating_system_id=self.operating_system_id,
            operating_system=self.operating_system,
            uptime=self.uptime,
            node_groups=self.node_groups,
            tags=self.tags,
            guest_vms=self.guest_vms,
            hypervisor=self.hypervisor,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
            )


class HardwareProfile(Base):
    __tablename__ = 'hardware_profiles'
    hardware_profile_id   = Column(Integer, primary_key=True, nullable=False)
    model                 = Column(Text, nullable=False)
    manufacturer          = Column(Text, nullable=False)
    created               = Column(TIMESTAMP, nullable=False)
    updated               = Column(TIMESTAMP, nullable=False)
    updated_by            = Column(Text, nullable=False)

    @hybrid_method
    def get_hardware_profile_id(self, manufacturer, model):
        q = DBSession.query(HardwareProfile)
        q = q.filter(HardwareProfile.manufacturer == '%s' % manufacturer)
        q = q.filter(HardwareProfile.model == '%s' % model)
        try:
            h = q.one()
            return h.hardware_profile_id
        except:
            return None

    def __json__(self, request):
        return dict(
            hardware_profile_id=self.hardware_profile_id,
            model=self.model,
            manufacturer=self.manufacturer,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
#            created=self.created.isoformat(),
#            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )


class OperatingSystem(Base):
    __tablename__ = 'operating_systems'
    operating_system_id   = Column(Integer, primary_key=True, nullable=False)
    variant               = Column(Text, nullable=False)
    version_number        = Column(Text, nullable=False)
    architecture          = Column(Text, nullable=False)
    description           = Column(Text, nullable=False)
    created               = Column(TIMESTAMP, nullable=False)
    updated               = Column(TIMESTAMP, nullable=False)
    updated_by            = Column(Text, nullable=False)

    def __json__(self, request):
        return dict(
            operating_system_id=self.operating_system_id,
            variant=self.variant,
            version_number=self.version_number,
            architecture=self.architecture,
            description=self.description,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
#            created=self.created.isoformat(),
#            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )

    @hybrid_method
    def get_operating_system_id(self, variant, version_number, architecture):
        q = DBSession.query(OperatingSystem)
        q = q.filter(OperatingSystem.variant == '%s' % variant)
        q = q.filter(OperatingSystem.version_number == '%s' % version_number)
        q = q.filter(OperatingSystem.rchitecture == '%s' % architecture)
        return q.one()


class NodeGroupAssignment(Base):
    __tablename__               = 'node_group_assignments'
    node_group_assignment_id    = Column(Integer, primary_key=True, nullable=False)
    node_id                     = Column(Integer, ForeignKey('nodes.node_id'), nullable=False)
    node_group_id               = Column(Integer, ForeignKey('node_groups.node_group_id'), nullable=False)
    updated_by                  = Column(Text, nullable=False)
    created                     = Column(TIMESTAMP, nullable=False)
    updated                     = Column(TIMESTAMP, nullable=False)
    node                        = relationship("Node", backref=backref('node_group_assignments'))

    def __json__(self, request):
        return dict(
            node_group_assignment_id=self.node_group_assignment_id,
            node_id=self.node_id,
            node_group_id=self.node_group_id,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
#            node=self.node,
            )


class NodeGroup(Base):
    __tablename__          = 'node_groups'
    node_group_id          = Column(Integer, primary_key=True, nullable=False)
    node_group_name        = Column(Text, nullable=False)
    node_group_owner       = Column(Text, nullable=False)
    description            = Column(Text, nullable=False)
    created                = Column(TIMESTAMP, nullable=False)
    updated                = Column(TIMESTAMP, nullable=False)
    updated_by             = Column(Text, nullable=False)
    node_group_assignments = relationship("NodeGroupAssignment", backref=backref('node_groups'),
                                          lazy="dynamic")

    @hybrid_property
    def tags(self):
        tags = []
        for a in self.tag_node_group_assignments:
            # Test to make sure the node group wasn't deleted after the
            # assignment was made
            if a.tags:
                tags.append(a.tags.__json__(self))
        return tags


    @hybrid_method
    def get_node_group_id(self, node_group_name):
        q = DBSession.query(NodeGroup)
        q = q.filter(NodeGroup.node_group_name == '%s' % node_group_name)
        return q.one()


    def __json__(self, request):
        return dict(
            node_group_id=self.node_group_id,
            node_group_name=self.node_group_name,
            node_group_owner=self.node_group_owner,
            description=self.description,
            tags=self.tags,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
            )


class Tag(Base):
    __tablename__                 = 'tags'
    tag_id                        = Column(Integer, primary_key=True, nullable=False)
    tag_name                      = Column(Text, nullable=False)
    tag_value                     = Column(Text, nullable=False)
    created                       = Column(TIMESTAMP, nullable=False)
    updated                       = Column(TIMESTAMP, nullable=False)
    updated_by                    = Column(Text, nullable=False)
    tag_node_assignments          = relationship("TagNodeAssignment", backref=backref('tags'),
                                                 lazy="dynamic")
    tag_node_group_assignments    = relationship("TagNodeGroupAssignment", backref=backref('tags'),
                                                 lazy="dynamic")

    def __json__(self, request):
        return dict(
            tag_id=self.tag_id,
            tag_name=self.tag_name,
            tag_value=self.tag_value,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
            )


class TagNodeAssignment(Base):
    __tablename__             = 'tag_node_assignments'
    tag_node_assignment_id    = Column(Integer, primary_key=True, nullable=False)
    tag_id                    = Column(Integer, ForeignKey('tags.tag_id'), nullable=False)
    node_id                   = Column(Integer, ForeignKey('nodes.node_id'), nullable=False) # Clunky
    updated_by                = Column(Text, nullable=False)
    created                   = Column(TIMESTAMP, nullable=False)
    updated                   = Column(TIMESTAMP, nullable=False)
    node                      = relationship("Node", backref=backref('tag_node_assignments'))

    def __json__(self, request):
        return dict(
            tag_node_assignment_id=self.tag_node_assignment_id,
            tag_id=self.tag_id,
            node_id=self.node_id,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
            )


class TagNodeGroupAssignment(Base):
    __tablename__                   = 'tag_node_group_assignments'
    tag_node_group_assignment_id    = Column(Integer, primary_key=True, nullable=False)
    tag_id                          = Column(Integer, ForeignKey('tags.tag_id'), nullable=False)
    node_group_id                   = Column(Integer, ForeignKey('node_groups.node_group_id'), nullable=False) # Clunky
    updated_by                      = Column(Text, nullable=False)
    created                         = Column(TIMESTAMP, nullable=False)
    updated                         = Column(TIMESTAMP, nullable=False)
    node_group                      = relationship("NodeGroup", backref=backref('tag_node_group_assignments'))

    def __json__(self, request):
        return dict(
            tag_node_group_assignment_id=self.tag_node_group_assignment_id,
            tag_id=self.tag_id,
            node_group_id=self.node_group_id,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
            updated_by=self.updated_by,
            )


class Status(Base):
    __tablename__ = 'statuses'
    status_id        = Column(Integer, primary_key=True, nullable=False)
    status_name      = Column(Text, nullable=False)
    description      = Column(Text, nullable=False)
    created          = Column(TIMESTAMP, nullable=False)
    updated          = Column(TIMESTAMP, nullable=False)
    updated_by       = Column(Text, nullable=False)

    @hybrid_method
    def get_status_id(self, status_name):
        q = DBSession.query(Status)
        q = q.filter(Status.status_name == status_name)
        try:
            s = q.one()
            return s.status_id
        except:
            return None

    def __json__(self, request):
        return dict(
            status_id=self.status_id,
            status_name=self.status_name,
            description=self.description,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
#            created=self.created.isoformat(),
#            updated=self.updated.isoformat(),
            updated_by=self.updated_by,
            )


class HypervisorVmAssignment(Base):
    __tablename__                   = 'hypervisor_vm_assignments'
    hypervisor_vm_assignment_id     = Column(Integer, primary_key=True, nullable=False)
    parent_node_id                  = Column(Integer, ForeignKey('nodes.node_id'), nullable=False)
    child_node_id                   = Column(Integer, ForeignKey('nodes.node_id'), nullable=False)
    updated_by                      = Column(Text, nullable=False)
    created                         = Column(TIMESTAMP, nullable=False)
    updated                         = Column(TIMESTAMP, nullable=False)

    # FIXME: Can't get this to work with backref, so have to do shenanigans
    # in the Node class.
    parent_node = relationship("Node", foreign_keys=[parent_node_id], backref='hva_parent')
    child_node = relationship("Node", foreign_keys=[child_node_id], backref='hva_child')
    #parent_node = relationship("Node", foreign_keys=[parent_node_id], backref=backref('hva_parent'))
    #child_node = relationship("Node", foreign_keys=[child_node_id], backref=backref('hva_child'))

    def __json__(self, request):

        # FIXME: The DB should be cleaning these up.
        try:
            hypervisor_name = self.parent_node.node_name
        except AttributeError:
            hypervisor_name = 'hypervisor_deleted'

        try:
            vm_name = self.child_node.node_name
        except AttributeError:
            vm_name = 'vm_deleted'

        return dict(
            hypervisor_vm_assignment_id=self.hypervisor_vm_assignment_id,
            parent_node_id=self.parent_node_id,
            parent_node_name=hypervisor_name,
            child_node_id=self.child_node_id,
            child_node_name=vm_name,
            created=_localize_date(self.created),
            updated=_localize_date(self.updated),
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


