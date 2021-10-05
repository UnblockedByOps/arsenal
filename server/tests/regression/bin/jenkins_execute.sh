#!/bin/bash -e
#
# Script for the jenkins execute shell to orhcestrate the test.

set -o pipefail
REGRESSION_DIR="${WORKSPACE}/server/tests/regression"

if [ "$ARSENAL_VERSION" == 'latest' ] ; then
    ARSENAL_VERSION=''
elif [ "$ARSENAL_VERSION" == 'dev' ] ; then
    ARSENAL_VERSION=' --pre'
else
    ARSENAL_VERSION="==${ARSENAL_VERSION}"
fi

if [ ! -f "${WORKSPACE}/venv/bin/activate" ]; then
  echo -e "\n***\n***\n*** Creating virtualenv for running docker images...\n***\n***\n"
  /opt/rh/rh-python36/root/bin/virtualenv -q ${WORKSPACE}/venv
  source ${WORKSPACE}/venv/bin/activate
  pip install -U pip setuptools && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple paramiko && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple docker-compose && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple rp-retry==2.0 && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple ruamel.yaml && \
  pip freeze | tee ${WORKSPACE}/venv/version.txt
fi

source ${WORKSPACE}/venv/bin/activate
cd ${REGRESSION_DIR}/docker

echo -e "\nFinal arsenal version: $ARSENAL_VERSION"

if [ "$REBUILD_CONTAINERS" = true ] ; then
  echo -e "\n***\n***\n*** Removing existing docker containers...\n***\n***\n"
  docker-compose rm -f -s
  echo 'Done.'
fi

if [ "$REMOVE_IMAGES" = true ] ; then
  echo -e "\n***\n***\n*** Removing existing docker images...\n***\n***\n"
  docker-compose down --rmi all
  echo 'Done.'
fi

FG_OPTS='-d'
if [ "$FOREGROUND_DOCKER" = true ] ; then
    FG_OPTS=''
fi

echo -e "\n***\n***\n*** Running docker-compose...\n***\n***\n"
docker-compose build
docker-compose up ${FG_OPTS}
echo -e "\n***\n***\n*** docker-compose complete.\n***\n***\n"

echo -e "\n***\n***\n*** Running test harness...\n***\n***\n"
cd ${REGRESSION_DIR}
python bin/api.py -t conf/api_test_cases.yaml -r ${TESTS_TO_RUN}
echo -e "\n***\n***\n*** Test harness complete.\n***\n***\n"

cd ${REGRESSION_DIR}/docker
echo -e "\n***\n***\n*** Shutting down docker images...\n***\n***\n"
docker-compose down
echo -e "\n***\n***\n*** Docker images shut down.\n***\n***\n"
