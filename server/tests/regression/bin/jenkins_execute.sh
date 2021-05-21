#!/bin/bash -e
#
# Script for the jenkins execute shell to orhcestrate the test.

set -o pipefail
REGRESSION_DIR="${WORKSPACE}/server/tests/regression"

if [ ! -f "${WORKSPACE}/venv/bin/activate" ]; then
  echo -e "\nCreating virtualenv...\n"
  /opt/rh/rh-python36/root/bin/virtualenv -q ${WORKSPACE}/venv
  source ${WORKSPACE}/venv/bin/activate
  pip install -U pip setuptools && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple alembic && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple paramiko && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple docker-compose && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple rp-retry==2.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple ruamel.yaml && \
  pip freeze | tee ${WORKSPACE}/venv/version.txt
fi

source ${WORKSPACE}/venv/bin/activate

cd ${WORKSPACE}/server/
CREATE_FILE="${WORKSPACE}/server/tests/regression/docker/mysql_init/create.sql"
echo 'use arsenal;' >  ${CREATE_FILE}
alembic -c development.ini upgrade head --sql >>  ${CREATE_FILE}

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
