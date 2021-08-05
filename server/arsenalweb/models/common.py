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
import datetime
from passlib.hash import sha512_crypt
from pytz import timezone
import pyramid
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    TIMESTAMP,
    Table,
    Text,
    VARCHAR,
    text,
)
from sqlalchemy.dialects.mysql import (
    INTEGER,
    MEDIUMINT,
)
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship

from .meta import Base

LOG = logging.getLogger(__name__)

NO_CONVERT = [
    'account_id',
    'elevation',
    'postal_code',
]


# Common functions
def check_null_string(obj):
    '''Check for null string for json object.'''

    if not obj:
        return ''
    return obj

def check_null_dict(obj):
    '''Check for null dict for json object.'''

    if not obj:
        return {}

    return obj

def localize_date(datetime_obj):
    '''Localize dates stored in UTC in the DB to a timezone.'''

    try:
        registry = pyramid.threadlocal.get_current_registry()
        settings = registry.settings
        zone = settings['arsenal.timezone']
        time_format = "%Y-%m-%d %H:%M:%S %Z%z"
        LOG.debug('Time zone is: %s', zone)
        localized = datetime_obj.astimezone(timezone(zone))
        return localized.strftime(time_format)
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
        if isinstance(p_type, datetime.datetime):
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


# Many to many association tables.
local_user_group_assignments = Table('local_user_group_assignments',
                                      Base.metadata,
                                      Column('user_id',
                                             MEDIUMINT(9, unsigned=True),
                                             ForeignKey('users.id')),
                                      Column('group_id',
                                             MEDIUMINT(9, unsigned=True),
                                             ForeignKey('groups.id'))
                                     )

group_perm_assignments = Table('group_perm_assignments',
                                Base.metadata,
                                Column('group_id',
                                       MEDIUMINT(9, unsigned=True),
                                       ForeignKey('groups.id')),
                                Column('perm_id',
                                       MEDIUMINT(9, unsigned=True),
                                       ForeignKey('group_perms.id'))
                               )

hypervisor_vm_assignments = Table('hypervisor_vm_assignments',
                                  Base.metadata,
                                  Column('hypervisor_id',
                                         INTEGER(unsigned=True),
                                         ForeignKey('nodes.id')),
                                  Column('guest_vm_id',
                                         INTEGER(unsigned=True),
                                         ForeignKey('nodes.id'))
                                 )

network_interface_assignments = Table('network_interface_assignments',
                                      Base.metadata,
                                      Column('node_id',
                                             INTEGER(unsigned=True),
                                             ForeignKey('nodes.id')),
                                      Column('network_interface_id',
                                             INTEGER(unsigned=True),
                                             ForeignKey('network_interfaces.id'))
                                     )

node_group_assignments = Table('node_group_assignments',
                               Base.metadata,
                               Column('node_id',
                                      INTEGER(unsigned=True),
                                      ForeignKey('nodes.id')),
                               Column('node_group_id',
                                      INTEGER(unsigned=True),
                                      ForeignKey('node_groups.id'))
                              )

tag_data_center_assignments = Table('tag_data_center_assignments',
                                    Base.metadata,
                                    Column('tag_id',
                                           INTEGER(unsigned=True),
                                           ForeignKey('tags.id')),
                                    Column('data_center_id',
                                           INTEGER(unsigned=True),
                                           ForeignKey('data_centers.id'))
                                   )

tag_node_assignments = Table('tag_node_assignments',
                             Base.metadata,
                             Column('tag_id',
                                    INTEGER(unsigned=True),
                                    ForeignKey('tags.id')),
                             Column('node_id',
                                    INTEGER(unsigned=True),
                                    ForeignKey('nodes.id'))
                            )

tag_node_group_assignments = Table('tag_node_group_assignments',
                                   Base.metadata,
                                   Column('tag_id',
                                          INTEGER(unsigned=True),
                                          ForeignKey('tags.id')),
                                   Column('node_group_id',
                                          INTEGER(unsigned=True),
                                          ForeignKey('node_groups.id'))
                                  )

tag_physical_device_assignments = Table('tag_physical_device_assignments',
                                        Base.metadata,
                                        Column('tag_id',
                                               INTEGER(unsigned=True),
                                               ForeignKey('tags.id')),
                                        Column('physical_device_id',
                                               INTEGER(unsigned=True),
                                               ForeignKey('physical_devices.id'))
                                       )


class User(Base):
    '''Arsenal User object.'''

    __tablename__ = 'users'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(MEDIUMINT(9, unsigned=True), primary_key=True, nullable=False)
    name = Column(Text, nullable=False) # email address
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    salt = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    groups = relationship('Group',
                    secondary='local_user_group_assignments',
                    backref='users',
                    lazy='dynamic')
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)

    def check_password(self, password):
        '''Check if the user's password matches what's in the DB.'''

        LOG.debug('Checking password against local DB...')
        try:
            if sha512_crypt.verify(password, self.password):
                LOG.debug('Successfully authenticated via local DB')
                return True
        except Exception as ex:
            LOG.error('%s (%s)', Exception, ex)

        LOG.debug('Bad password via local DB for user: %s', self.name)
        return False

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
                    id=self.id,
                    name=self.name,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    groups=get_name_id_list(self.groups),
                    created=localize_date(self.created),
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return id, and name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'groups' in my_fields:
                resp['groups'] = get_name_id_list(self.groups)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only id, and name.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


Index('idx_user_name_unique', User.name, unique=True, mysql_length=255)


class Group(Base):
    '''Arsenal Group object.'''

    __tablename__ = 'groups'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(MEDIUMINT(9, unsigned=True), primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    group_perms = relationship('GroupPerm',
                    secondary='group_perm_assignments',
                    backref='groups',
                    lazy='dynamic')
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)

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
                    id=self.id,
                    name=self.name,
                    group_perms=get_name_id_list(self.group_perms),
                    users=get_name_id_list(self.users),
                    created=localize_date(self.created),
                    updated=self.updated,
                    updated_by=self.updated_by,
                    )

                return jsonify(all_fields)

            # Always return id, and name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')

            # Backrefs are not in the instance dict, so we handle them here.
            if 'users' in my_fields:
                resp['users'] = get_name_id_list(self.users)

            if 'group_perms' in my_fields:
                resp['group_perms'] = get_name_id_list(self.group_perms)

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only id, and name.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


Index('idx_group_name_unique', Group.name, unique=True, mysql_length=255)


class GroupPerm(Base):
    '''Arsenal GroupPerm object.'''

    __tablename__ = 'group_perms'
    __table_args__ = (
        {
            'mysql_charset':'utf8',
            'mysql_collate': 'utf8_bin',
            'mariadb_charset':'utf8',
            'mariadb_collate': 'utf8_bin',
        }
    )

    id = Column(MEDIUMINT(9, unsigned=True), primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "GroupPerm(id='%s', name='%s', )" % (self.id, self.name)

    @hybrid_method
    def get_group_perm_id(self, perm_name):
        '''Convert the perm name to the id.'''

        query = DBSession.query(GroupPerm)
        query = query.filter(GroupPerm.name == '%s' % perm_name)
        return query.one()

    def __json__(self, request):
        try:
            fields = request.params['fields']

            if fields == 'all':

                all_fields = dict(
                    id=self.id,
                    name=self.name,
                    created=localize_date(self.created),
                    )

                return jsonify(all_fields)

            # Always return id, and name, then return whatever
            # additional fields are asked for.
            resp = get_name_id_dict([self])

            my_fields = fields.split(',')

            resp.update((key, getattr(self, key)) for key in my_fields if
                        key in self.__dict__)

            return jsonify(resp)

        # Default to returning only id, and name.
        except KeyError:
            resp = get_name_id_dict([self])

            return resp


Index('idx_group_perms_unique', GroupPerm.name, unique=True, mysql_length=255)


class BaseAudit(Base):
    '''Arsenal BaseAudit object. Allows for overriding on other Audit classes.'''

    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False)
    object_id = Column(Integer, nullable=False)
    field = Column(Text, nullable=False)
    old_value = Column(Text, nullable=False)
    new_value = Column(Text, nullable=False)
    created = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                     nullable=False)
    updated_by = Column(VARCHAR(255), nullable=False)

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
