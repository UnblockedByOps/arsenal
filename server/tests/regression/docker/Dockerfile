FROM docker.rp-core.com/devops/docker_centos_base:4_7.4

EXPOSE 80
EXPOSE 443
CMD ["apachectl", "-D", "FOREGROUND"]

COPY conf/arsenal.wsgi /app/arsenal_web/conf/arsenal.wsgi
COPY conf/arsenal_secrets.ini /app/arsenal_web/conf/arsenal_secrets.ini
COPY conf/arsenal-web.ini /app/arsenal_web/conf/arsenal-web.ini
RUN yum install -y \
  httpd \
  mod_wsgi \
  mod_ssl \
  rh-python36 \
  gcc \
  openldap-devel
COPY conf/arsenal-wsgi.conf /etc/httpd/conf.d/arsenal-wsgi.conf
COPY conf/ssl/server.crt /etc/pki/tls/certs/server.crt
COPY conf/ssl/server.key /etc/pki/tls/private/server.key
RUN /opt/rh/rh-python36/root/bin/virtualenv --no-setuptools /app/arsenal_web/venv && \
  source /app/arsenal_web/venv/bin/activate && \
  pip install setuptools && \
  pip install --upgrade pip && \
  pip install https://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-1.2.3.tar.gz

# Valid values for ARSENAL_VERSION are as follows:
#
# If you're testing a development version (note the leading space):
#   ' --pre'
#
# If you're testing a tag:
#   '==1.2'
#
ARG ARSENAL_VERSION
RUN source /app/arsenal_web/venv/bin/activate && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple arsenalweb${ARSENAL_VERSION}
