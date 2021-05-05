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

NO_CONVERT = [
    'account_id',
    'elevation',
    'postal_code',
]


# Many to many association tables.
local_user_group_assignments = Table('local_user_group_assignments',
                                      Base.metadata,
                                      Column('user_id',
                                             Integer,
                                             ForeignKey('users.user_id')),
                                      Column('group_id',
                                             Integer,
                                             ForeignKey('groups.group_id'))
                                     )

group_perm_assignments = Table('group_perm_assignments',
                                Base.metadata,
                                Column('group_id',
                                       Integer,
                                       ForeignKey('groups.group_id')),
                                Column('perm_id',
                                       Integer,
                                       ForeignKey('group_perms.perm_id'))
                               )

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

tag_physical_device_assignments = Table('tag_physical_device_assignments',
                                        Base.metadata,
                                        Column('physical_device_id',
                                               Integer,
                                               ForeignKey('physical_devices.id')),
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
            if param in NO_CONVERT:
                p_type = obj.get(param)

                LOG.debug('Using raw db value for param: {0} value: {1}'.format(param,
                                                                                p_type))
            else:
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
    groups = relationship('Group',
                    secondary='local_user_group_assignments',
                    backref='users',
                    lazy='dynamic')
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)

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

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    user_id=self.user_id,
                    user_name=self.user_name,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    groups=get_name_id_list(self.groups,
                                            default_keys=[
                                                'group_id',
                                                'group_name'
                                            ]),
                    created=localize_date(self.created),
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return user_id, and user_name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self], default_keys=[
                                                             'user_id',
                                                             'user_name',
                                                         ])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'group' in my_fields:
                resp['group'] = get_name_id_list(self.group)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only user_id, and user_name.
        except KeyError:
            resp = get_name_id_dict([self], default_keys=[
                                                             'user_id',
                                                             'user_name',
                                                         ])

            return resp


class Group(Base):
    '''Arsenal Group object.'''

    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, nullable=False)
    group_name = Column(Text, nullable=False)
    group_perms = relationship('GroupPerm',
                    secondary='group_perm_assignments',
                    backref='groups',
                    lazy='dynamic')
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=False)

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

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    group_id=self.group_id,
                    group_name=self.group_name,
                    group_perms=get_name_id_list(self.group_perms,
                                                 default_keys=[
                                                     'perm_id',
                                                     'perm_name'
                                                 ]),
                    created=localize_date(self.created),
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return user_id, and user_name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self], default_keys=[
                                                             'group_id',
                                                             'group_name',
                                                         ])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'user' in my_fields:
                resp['user'] = get_name_id_list(self.user)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only user_id, and user_name.
        except KeyError:
            resp = get_name_id_dict([self], default_keys=[
                                                             'group_id',
                                                             'group_name',
                                                         ])

            return resp


class GroupPerm(Base):
    '''Arsenal GroupPerm object.'''

    __tablename__ = 'group_perms'
    perm_id = Column(Integer, primary_key=True, nullable=False)
    perm_name = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "GroupPerm(perm_id='%s', perm_name='%s', )" % (self.perm_id, self.perm_name)

    @hybrid_method
    def get_group_perm_id(self, perm_name):
        '''Convert the perm name to the id.'''

        query = DBSession.query(GroupPerm)
        query = query.filter(GroupPerm.perm_name == '%s' % perm_name)
        return query.one()

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    perm_id=self.perm_id,
                    perm_name=self.perm_name,
                    created=localize_date(self.created),
                    )

                return jsonify(all_fields)

            # Always return user_id, and user_name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self], default_keys=[
                                                             'perm_id',
                                                             'perm_name',
                                                         ])

            my_fields = fields.split(',')

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only user_id, and user_name.
        except KeyError:
            resp = get_name_id_dict([self], default_keys=[
                                                             'perm_id',
                                                             'perm_name',
                                                         ])

            return resp
