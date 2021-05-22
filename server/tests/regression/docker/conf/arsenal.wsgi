from pyramid.paster import get_app, setup_logging
ini_path = '/app/arsenal_web/conf/arsenal-web.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
