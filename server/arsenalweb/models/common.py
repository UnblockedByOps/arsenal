'''Arsenal common DB Model'''
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
from datetime import datetime
import arrow
from dateutil import tz
import pyramid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    TIMESTAMP,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
LOG = logging.getLogger(__name__)


# Many to many association tables.
hypervisor_vm_assignments = Table('hypervisor_vm_assignments',
                                  Base.metadata,
                                  Column('hypervisor_id',
                                         Integer,
                                         ForeignKey('nodes.id')),
                                  Column('guest_vm_id',
                                         Integer,
                                         ForeignKey('nodes.id'))
                                 )

network_interface_assignments = Table('network_interface_assignments',
                                      Base.metadata,
                                      Column('node_id',
                                             Integer,
                                             ForeignKey('nodes.id')),
                                      Column('network_interface_id',
                                             Integer,
                                             ForeignKey('network_interfaces.id'))
                                     )

node_group_assignments = Table('node_group_assignments',
                               Base.metadata,
                               Column('node_id',
                                      Integer,
                                      ForeignKey('nodes.id')),
                               Column('node_group_id',
                                      Integer,
                                      ForeignKey('node_groups.id'))
                              )

tag_data_center_assignments = Table('tag_data_center_assignments',
                                    Base.metadata,
                                    Column('data_center_id',
                                           Integer,
                                           ForeignKey('data_centers.id')),
                                    Column('tag_id',
                                           Integer,
                                           ForeignKey('tags.id'))
                                   )

tag_node_assignments = Table('tag_node_assignments',
                             Base.metadata,
                             Column('node_id',
                                    Integer,
                                    ForeignKey('nodes.id')),
                             Column('tag_id',
                                    Integer,
                                    ForeignKey('tags.id'))
                            )

tag_node_group_assignments = Table('tag_node_group_assignments',
                                   Base.metadata,
                                   Column('node_group_id',
                                          Integer,
                                          ForeignKey('node_groups.id')),
                                   Column('tag_id',
                                          Integer,
                                          ForeignKey('tags.id'))
                                  )

# Common functions
def check_null_string(obj):
    '''Check for null string for json object.'''

    if not obj:
        return ''
    else:
        return obj

def check_null_dict(obj):
    '''Check for null dict for json object.'''

    if not obj:
        return {}
    else:
        return obj

def localize_date(obj):
    '''Localize dates stored in UTC in the DB to a timezone.'''

    try:
        utc = arrow.get(obj)
        registry = pyramid.threadlocal.get_current_registry()
        settings = registry.settings
        zone = settings['arsenal.timezone']
        LOG.debug('Time zone is: {0}'.format(zone))
        return utc.to(tz.gettz(zone)).format('YYYY-MM-DD HH:mm:ss')
    except:
        return 'Datetime object'

def jsonify(obj):
    '''Convert an object or dict to json.'''

    LOG.debug('jsonify()')
    resp = {}
    try:
        convert = obj.__dict__
    except AttributeError:
        convert = obj
    except:
        raise

    for param in convert:
        if param.startswith('_'):
            continue
        try:
            try:
                p_type = int(getattr(obj, param))
            except (ValueError, TypeError):
                p_type = getattr(obj, param)
        except AttributeError:
            try:
                p_type = int(obj.get(param))
            except (ValueError, TypeError):
                p_type = obj.get(param)

        # Handle datetime objects
        if isinstance(p_type, datetime):
            date = localize_date(p_type)
            resp[param] = date
        else:
            resp[param] = p_type

    return resp

def get_name_id_dict(objs, default_keys=None, extra_keys=None):
    '''Take a list of one object and convert them to json. Returns a dict. Have
    to iterate over a list to get SQL Alchemy to execute the query.'''

    if not default_keys:
        default_keys = ['name', 'id']

    LOG.debug('get_name_id_dict()')
    resp = {}
    for obj in objs:
        item = {}
        for key in default_keys:
            try:
                my_val = getattr(obj, key)
            except AttributeError:
                my_val = 'None'
            except:
                raise
            item[key] = my_val
        if extra_keys:
            for key in extra_keys:
                LOG.debug('Working on extra key: {0}'.format(key))
                try:
                    my_val = getattr(obj, key)
                except AttributeError:
                    my_val = 'None'
                except:
                    raise
                item[key] = my_val

        resp = jsonify(item)

    return resp

def get_name_id_list(objs, default_keys=None, extra_keys=None):
    '''Take a list of one or more objects and convert them to json. Returns a
    list.'''

    if not default_keys:
        default_keys = ['name', 'id']

    LOG.debug('get_name_id_list()')
    resp = []
    for obj in objs:
        item = {}
        for key in default_keys:
            item[key] = getattr(obj, key)
        if extra_keys:
            for key in extra_keys:
                # Preserve integers in tag values.
                if key == 'value':
                    try:
                        item[key] = int(getattr(obj, key))
                    except ValueError:
                        item[key] = getattr(obj, key)
                else:
                    item[key] = getattr(obj, key)

        resp.append(jsonify(item))

    return resp


# Base classes
class BaseAudit(Base):
    '''Arsenal BaseAudit object. Allows for overriding on other Audit classes.'''

    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False)
    object_id = Column(Integer, nullable=False)
    field = Column(Text, nullable=False)
    old_value = Column(Text, nullable=False)
    new_value = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated_by = Column(Text, nullable=False)

    def __json__(self, request):
        return dict(
            id=self.id,
            object_id=self.object_id,
            field=self.field,
            old_value=self.old_value,
            new_value=self.new_value,
            created=localize_date(self.created),
            updated_by=self.updated_by,
            )


class User(Base):
    '''Arsenal User object.'''

    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(Text, nullable=False) # email address
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    salt = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)

    @hybrid_method
    def get_all_assignments(self):
        '''Get all group assignents for the user.'''

        groups = []
        for assign in self.local_user_group_assignments:
            groups.append(assign.group.group_name)
        return groups

    @hybrid_property
    def localize_date_created(self):
        '''Return localized created datetime object.'''
        local = localize_date(self.created)
        return local

    @hybrid_property
    def localize_date_updated(self):
        '''Return localized updated datetime object.'''
        local = localize_date(self.updated)
        return local


class LocalUserGroupAssignment(Base):
    '''Arsenal LocalUserGroupAssignment object.'''

    __tablename__ = 'local_user_group_assignments'
    user_group_assignment_id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    user = relationship('User', backref=backref('local_user_group_assignments'))
    group = relationship('Group', backref=backref('local_user_group_assignments'))


class Group(Base):
    '''Arsenal Group object.'''

    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, nullable=False)
    group_name = Column(Text, nullable=False)
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)

    @hybrid_method
    def get_all_assignments(self):
        '''Get all permissions a group is assigned to.'''

        group_assign = []
        for assign in self.group_perm_assignments:
            group_assign.append(assign.group_perms.perm_name)
        return group_assign

    @hybrid_property
    def localize_date_created(self):
        '''Return localized created datetime object.'''
        local = localize_date(self.created)
        return local

    @hybrid_property
    def localize_date_updated(self):
        '''Return localized updated datetime object.'''
        local = localize_date(self.updated)
        return local


class GroupPermAssignment(Base):
    '''Arsenal GroupPermAssignment object.'''

    __tablename__ = 'group_perm_assignments'
    group_assignment_id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    perm_id = Column(Integer, ForeignKey('group_perms.perm_id'), nullable=False)
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)
    group = relationship('Group', backref=backref('group_perm_assignments'))

    @hybrid_method
    def get_assignments_by_group(self, group_name):
        '''Return a list of permission assignments by group name.'''

        query = DBSession.query(GroupPermAssignment)
        query = query.join(Group, GroupPermAssignment.group_id == Group.group_id)
        query = query.filter(Group.group_name == group_name)
        return query.all()

    @hybrid_method
    def get_assignments_by_perm(self, perm_name):
        '''Return a list of permission assignments by permission name.'''

        query = DBSession.query(GroupPermAssignment)
        query = query.join(Group, GroupPermAssignment.group_id == Group.group_id)
        query = query.join(GroupPerm, GroupPermAssignment.perm_id == GroupPerm.perm_id)
        query = query.filter(GroupPerm.perm_name == perm_name)
        return query.all()


class GroupPerm(Base):
    '''Arsenal GroupPerm object.'''

    __tablename__ = 'group_perms'
    perm_id = Column(Integer, primary_key=True, nullable=False)
    perm_name = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    group_perm_assignments = relationship('GroupPermAssignment', backref=backref('group_perms'),
                                          order_by=GroupPermAssignment.created.desc,
                                          lazy='dynamic')

    def __repr__(self):
        return "GroupPerm(perm_id='%s', perm_name='%s', )" % (self.perm_id, self.perm_name)

    @hybrid_method
    def get_all_assignments(self):
        '''Return a list of all group permission assignments.'''
        perm_assign = []
        for assign in self.group_perm_assignments:
            perm_assign.append(assign.group.group_name)
        return perm_assign

    @hybrid_method
    def get_group_perm_id(self, perm_name):
        '''Convert the perm name to the id.'''

        query = DBSession.query(GroupPerm)
        query = query.filter(GroupPerm.perm_name == '%s' % perm_name)
        return query.one()
