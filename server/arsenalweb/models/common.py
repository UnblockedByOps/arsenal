from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    TIMESTAMP,
    Table,
    Text,
    text,
)
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref


from .meta import Base


#class MyModel(Base):
#    __tablename__ = 'models'
#    id = Column(Integer, primary_key=True)
#    name = Column(Text)
#    value = Column(Integer)
#
#
#Index('my_index', MyModel.name, unique=True, mysql_length=255)
#
#class MyModel2(Base):
#    __tablename__ = 'models2'
#    id = Column(Integer, primary_key=True)
#    name = Column(Text)
#    value = Column(Integer)
#
#
#Index('my_index2', MyModel2.name, unique=True, mysql_length=255)

# Many to many association tables.
local_user_group_assignments = Table('local_user_group_assignments',
                                      Base.metadata,
                                      Column('user_id',
                                             Integer,
                                             ForeignKey('users.id')),
                                      Column('group_id',
                                             Integer,
                                             ForeignKey('groups.id'))
                                     )

group_perm_assignments = Table('group_perm_assignments',
                                Base.metadata,
                                Column('group_id',
                                       Integer,
                                       ForeignKey('groups.id')),
                                Column('perm_id',
                                       Integer,
                                       ForeignKey('group_perms.id'))
                               )

class User(Base):
    '''Arsenal User object.'''

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False) # email address
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    salt = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    groups = relationship('Group',
                    secondary='local_user_group_assignments',
                    backref='users',
                    lazy='dynamic')
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

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
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    group_perms = relationship('GroupPerm',
                    secondary='group_perm_assignments',
                    backref='groups',
                    lazy='dynamic')
    updated_by = Column(Text, nullable=False)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP,
                     server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

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
    id = Column(Integer, primary_key=True, nullable=False)
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
