FROM rockylinux:9.3.20231119
RUN dnf install -y python pkg-config gcc httpd.x86_64 mod_ssl.x86_64 python3-mod_wsgi.x86_64
RUN dnf install -y python-devel mariadb-devel openldap-devel --enablerepo=devel
RUN pip3 install virtualenv

RUN rm -f /etc/httpd/conf.d/*

RUN /usr/local/bin/virtualenv /app/arsenal_web/venv && \
  source /app/arsenal_web/venv/bin/activate && \
  pip3 install --upgrade setuptools==59.8.0 && \
  pip3 install --upgrade pip==24.2

ARG ARSENAL_VERSION=none
ENV ARSENAL_VERSION=$ARSENAL_VERSION
# FIXME: install from pypi
ADD dist/arsenalweb-$ARSENAL_VERSION-py2.py3-none-any.whl /app/arsenal_web/arsenalweb-$ARSENAL_VERSION-py2.py3-none-any.whl
RUN  source /app/arsenal_web/venv/bin/activate && \
  pip3 install  /app/arsenal_web/arsenalweb-$ARSENAL_VERSION-py2.py3-none-any.whl
  
RUN mkdir /app/arsenal_web/conf
RUN mkdir /app/arsenal_web/sconf
RUN mkdir /app/arsenal_web/hc

EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]
