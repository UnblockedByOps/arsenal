FROM docker.rp-core.com/devops/docker_centos_base:2_7.8

EXPOSE 80
EXPOSE 443
CMD ["/opt/rh/httpd24/root/usr/sbin/httpd", "-D", "FOREGROUND"]
#CMD ["/usr/bin/scl", "enable", "httpd24", "--" "/opt/rh/httpd24/root/usr/sbin/apachectl", "-D", "FOREGROUND"]

RUN yum install -y \
  gcc \
  httpd24-httpd \
  httpd24-mod_ssl \
  inotify-tools \
  mariadb-devel \
  openldap-devel \
  rh-python38 \
  rh-python38-python-devel \
  rh-python38-python-mod_wsgi
RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple virtualenv==20.4.7
COPY conf/arsenal.wsgi /app/arsenal_web/conf/arsenal.wsgi
COPY conf/arsenal_secrets.ini /app/arsenal_web/conf/arsenal_secrets.ini
COPY conf/arsenal-web.ini /app/arsenal_web/conf/arsenal-web.ini

COPY conf/arsenal-wsgi.conf /opt/rh/httpd24/root/etc/httpd/conf.d/arsenal-wsgi.conf

COPY conf/ssl/server.crt /etc/pki/tls/certs/server.crt
COPY conf/ssl/server.key /etc/pki/tls/private/server.key
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
#
ARG ARSENAL_VERSION
RUN source /app/arsenal_web/venv/bin/activate && \
  pip3 install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple arsenalweb${ARSENAL_VERSION}
