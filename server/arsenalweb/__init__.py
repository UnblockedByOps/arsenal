'''Arsenal Pyramid WSGI application.'''
import logging
import configparser
from pyramid.config import Configurator
from pyramid.renderers import JSON
import transaction
from .models import get_engine, get_session_factory, get_tm_session
from .models.common import User
from sqlalchemy import inspect as sa_inspect


LOG = logging.getLogger(__name__)


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

def lod_db_acls(settings):
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
    lod_db_acls(settings)

    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.include('.routes')
        config.include('.models')
        config.add_renderer('json', JSON(indent=2, sort_keys=True))
        config.scan()
    return config.make_wsgi_app()
