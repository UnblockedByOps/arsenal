'''Arsenal Pyramid WSGI application.'''
import logging
import time
import configparser
from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid.security import Allow, Authenticated
import transaction
from .models import get_engine, get_session_factory, get_tm_session
from .models.common import User
from .models.common import Group
from sqlalchemy import inspect as sa_inspect

LOG = logging.getLogger(__name__)


class RootFactory:
    '''Top level ACL class.'''

    # Additional ACLs loaded from the DB below
    __acl__ = [
        (Allow, Authenticated, ('view', 'tag_write', 'tag_delete'))
    ]
    def __init__(self, request):
        pass

def get_settings(global_config, settings):
    '''Read in settings from config files.'''

    LOG.debug('Reading secrets from file: %s', settings['arsenal.secrets_file'])

    mcp = configparser.ConfigParser()
    mcp.read(settings['arsenal.secrets_file'])
    for key, val in mcp.items("app:main"):
        settings[key] = val

    LOG.debug('Reading app:safe configuration from file: %s', settings['arsenal.secrets_file'])

    scp = configparser.SafeConfigParser()
    scp.read(global_config)
    for key, val in scp.items("app:safe"):
        settings[key] = val

    return settings

def get_db_session(settings):
    '''Load all the group based ACLs from the database at startup.'''

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        LOG.info('User : %s', dir(User.registry))

        query = dbsession.query(User)
        one = query.filter(User.name == 'admin').one()
        LOG.info('user id: %s', one.id)
        LOG.info('user name: %s', one.name)
        LOG.info('one first_name: %s', one.first_name)
        LOG.info('one last_name: %s', one.last_name)

def main(global_config, **settings):
    '''This function returns a Pyramid WSGI application.'''

    settings = get_settings(global_config['__file__'], settings)
    LOG.debug('Some setting: %s', settings['arsenal.node_hw_map.hibernating'])

    with Configurator(settings=settings, root_factory=RootFactory) as config:
        config.include('pyramid_chameleon')
        config.include('.security')
        config.include('.routes')
        config.include('.models')
        config.add_renderer('json', JSON(indent=2, sort_keys=True))

        # Load our groups and perms from the db and add them to the ACL. I
        # believe we can move this loader into the security policy if we ever
        # make changing perms a dynamic operation from the UI and no restart
        # would be required, but it would hit the DB for every permissions
        # check.
        max_retries = 10
        for retry in range(1, max_retries):
            try:

                # FIXME: Not sure this is best way to talk to the DB here
                engine = get_engine(settings)
                session_factory = get_session_factory(engine)
                with transaction.manager:
                    dbsession = get_tm_session(session_factory, transaction.manager)

                    resp = dbsession.query(Group).all()

                    for group in resp:
                        group_assign_names = [gp.name for gp in group.group_perms]
                        if group_assign_names:
                            group_assign_names = tuple(group_assign_names)
                            LOG.info('Adding perms for group: %s perms: %s', group.name, group_assign_names)
                            RootFactory.__acl__.append([Allow, 'group:' + group.name, group_assign_names])
            except Exception as ex:
                LOG.warning('Unable to load ACLs from database(%s of %s)! Exception: '
                         '%s', retry, max_retries, repr(ex))
                sleep_secs = 5
                LOG.warning('Sleeping %s seconds before retrying', sleep_secs)
                time.sleep(sleep_secs)
            else:
                break
        else:
            LOG.warning('Unable to load ACLs from database after %s retries! '
                        'Continuing in an ACL-less universe.', max_retries)

        config.scan()

    return config.make_wsgi_app()
