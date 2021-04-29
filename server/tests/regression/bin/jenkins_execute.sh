#!/bin/bash -e
#
# Script for the jenkins execute shell to orhcestrate the test.

set -o pipefail
REGRESSION_DIR="${WORKSPACE}/server/tests/regression"

if [ ! -f "${WORKSPACE}/venv/bin/activate" ]; then
  echo -e "\nCreating virtualenv...\n"
  /usr/bin/virtualenv -q ${WORKSPACE}/venv
  source ${WORKSPACE}/venv/bin/activate
  pip install -U pip==10.0.1 setuptools==44.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple PyNaCl==1.4.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple pyrsistent==0.16.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple attrs==19.3.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple cached-property==1.5.1 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple certifi==2020.6.20 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple cffi==1.14.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple chardet==3.0.4 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple cryptography==2.9.2 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple docker==4.2.2 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple paramiko==2.7.1 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple docker-compose==1.26.2 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple rp-retry==2.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple ruamel.yaml==0.16.10 && \
  pip freeze | tee ${WORKSPACE}/venv/version.txt
fi

source ${WORKSPACE}/venv/bin/activate
cd ${REGRESSION_DIR}/docker

if [ "$ARSENAL_VERSION" == 'latest' ] ; then
    ARSENAL_VERSION=''
elif [ "$ARSENAL_VERSION" == 'dev' ] ; then
    ARSENAL_VERSION=' --pre'
else
    ARSENAL_VERSION="==${ARSENAL_VERSION}"
fi

echo -e "\nFinal arsenal version: $ARSENAL_VERSION"

if [ "$REBUILD_CONTAINERS" = true ] ; then
  echo -e '\nRemoving existing docker containers...'
  docker-compose rm -f -s
  echo 'Done.'
fi

if [ "$REMOVE_IMAGES" = true ] ; then
  echo -e '\nRemoving existing docker images...'
  docker-compose down --rmi all
  echo 'Done.'
fi

FG_OPTS='-d'
if [ "$FOREGROUND_DOCKER" = true ] ; then
    FG_OPTS=''
fi

echo -e '\nRunning docker-compose...\n'
docker-compose build
docker-compose up ${FG_OPTS}
echo -e '\ndocker-compose complete.\n'

cd ${REGRESSION_DIR}
python bin/api.py -t conf/api_test_cases.yaml -r ${TESTS_TO_RUN}

cd ${REGRESSION_DIR}/docker
echo -e '\nShutting down docker images...\n'
docker-compose down
echo -e '\ndocker images shut down.\n'
