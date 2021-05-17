'''Arsenal Pyramid WSGI application.'''
import logging
import configparser
from pyramid.config import Configurator
import transaction
from .models import get_engine, get_session_factory, get_tm_session
#from .models.common import MyModel


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

def connect_db():
    '''Connect to the db here and do something.'''

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        query = dbsession.query(MyModel)
        one = query.filter(MyModel.name == 'one').one()
        LOG.info('one id: %s', one.id)
        LOG.info('one name: %s', one.name)
        LOG.info('one value: %s', one.value)


def main(global_config, **settings):
    '''This function returns a Pyramid WSGI application.'''

    settings = get_settings(global_config['__file__'], settings)
    LOG.debug('Some setting: %s', settings['arsenal.node_hw_map.hibernating'])

    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.include('.routes')
        config.include('.models')
        config.scan()
    return config.make_wsgi_app()
