import os
activate_this = "/app/arsenal_web/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

from pyramid.paster import get_app, setup_logging
ini_path = '/app/arsenal_web/conf/arsenal-web.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
