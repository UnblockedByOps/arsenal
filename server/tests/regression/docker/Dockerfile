FROM centos/httpd-24-centos7:20200326-cd65777
# FROM quay.io/centos7/httpd-24-centos7

#FROM docker.rp-core.com/devops/docker_centos_base:2_7.8
#FROM centos/httpd-24-centos7:20210517-40a7981

USER root

EXPOSE 80
EXPOSE 443
#CMD ["/opt/rh/httpd24/root/usr/sbin/httpd", "-D", "FOREGROUND"]
#CMD ["/opt/rh/httpd24/root/usr/sbin/apachectl", "-D", "FOREGROUND"]
#CMD ["/usr/sbin/service", "httpd24-httpd", "start"]
CMD ["/usr/bin/run-httpd"]

#RUN yum clean all
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

COPY conf/arsenal.wsgi /app/arsenal_web/conf/arsenal.wsgi
COPY conf/arsenal_secrets.ini /app/arsenal_web/conf/arsenal_secrets.ini
COPY conf/arsenal-web.ini /app/arsenal_web/conf/arsenal-web.ini
COPY conf/ssl/server.crt /etc/pki/tls/certs/server.crt
COPY conf/ssl/server.key /etc/pki/tls/private/server.key
#RUN rm -f /opt/rh/httpd24/root/etc/httpd/conf.d/*.conf
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

#RUN cp /opt/rh/httpd24/root/usr/lib64/libnghttp2-httpd24.so.14.4.1 /opt/rh/httpd24/root/usr/lib64/httpd/
#RUN ln -sf /opt/rh/httpd24/root/usr/lib64/httpd/libnghttp2-httpd24.so.14.4.1 /opt/rh/httpd24/root/usr/lib64/httpd/libnghttp2-httpd24.so.14

ARG ARSENAL_VERSION
RUN source /app/arsenal_web/venv/bin/activate && \
  pip3 install --trusted-host pypi.las2.fanops.net -i http://pypi.las2.fanops.net/nexus/repository/pypi-all/simple arsenalweb${ARSENAL_VERSION}
