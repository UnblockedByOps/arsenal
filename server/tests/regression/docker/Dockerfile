FROM docker.rp-core.com/magnite/docker_arsenalweb_base:2_master

COPY conf/arsenal.wsgi /app/arsenal_web/conf/arsenal.wsgi
COPY conf/arsenal_secrets.ini /app/arsenal_web/conf/arsenal_secrets.ini
COPY conf/arsenal-web.ini /app/arsenal_web/conf/arsenal-web.ini
COPY conf/ssl/server.crt /etc/pki/tls/certs/server.crt
COPY conf/ssl/server.key /etc/pki/tls/private/server.key
COPY conf/arsenal-wsgi.conf /opt/rh/httpd24/root/etc/httpd/conf.d/arsenal-wsgi.conf

RUN /opt/rh/rh-python38/root/usr/local/bin/virtualenv /app/arsenal_web/venv && \
  source /app/arsenal_web/venv/bin/activate && \
  pip3 install --upgrade setuptools && \
  pip3 install --upgrade pip

# Valid values for ARSENAL_VERSION are as follows:
#
# If you're testing a development version (note the leading space):
#   ' --pre'
#
# If you're testing a tag:
#   '==1.2'
ARG ARSENAL_VERSION
RUN source /app/arsenal_web/venv/bin/activate && \
  pip3 install --trusted-host pypi.las2.fanops.net -i http://pypi.las2.fanops.net/nexus/repository/pypi-all/simple arsenalweb${ARSENAL_VERSION}
