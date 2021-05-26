FROM docker.rp-core.com/devops/docker_centos_base:2_7.8

EXPOSE 80
EXPOSE 443
ENTRYPOINT ["/usr/local/bin/run-httpd24.sh"]
CMD ["httpd", "-DFOREGROUND"]

# When bash is started non-interactively, to run a shell script, for example it
# looks for this variable and source the content of this file. This will enable
# the SCL for all scripts without need to do 'scl enable'.
ENV BASH_ENV=/var/lib/httpd24/scl_enable \
    ENV=/var/lib/httpd24/scl_enable \
    PROMPT_COMMAND=". /var/lib/httpd24/scl_enable"

RUN yum clean all && \
    rm -f /etc/yum.repos.d/*.repo
ADD yum_repos /etc/yum.repos.d

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
RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --trusted-host pypi.las2.fanops.net -i http://pypi.las2.fanops.net/nexus/repository/pypi-all/simple virtualenv==20.4.7

COPY bin/run-httpd24.sh /usr/local/bin/run-httpd24.sh
RUN mkdir -p /var/lib/httpd24
COPY bin/scl_enable /var/lib/httpd24/scl_enable

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
