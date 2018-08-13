#!/bin/bash -e
#
# Script for the jenkins execute shell to orhcestrate the test.

set -o pipefail
REGRESSION_DIR="${WORKSPACE}/server/tests/regression"
CLIENT_DIR="${WORKSPACE}/client"
ARSENAL_SERVER="localhost:4443"

check_arsenal_ready () {
    # Make sure arsenal is up before proceeding.
    RETRY=1
    RETRIES=10
    until [ $RETRY -ge $RETRIES ] ; do
        echo "Checking to see if Arsenal docker container is responding ($RETRY of $RETRIES)..."
        HTTP_CODE=$(curl -k -o /dev/null -s -w "%{http_code}\n" https://${ARSENAL_SERVER}/api/nodes || true)
        if [ "${HTTP_CODE}" == '200' ] ; then
            echo "Arsenal is ready: ${HTTP_CODE}"
            return
        fi
        RETRY=$[$RETRY+1]
        sleep 5
    done
    echo "Arsenal not ready after ${RETRIES} retries. Unable to continue."
    exit 1

}

if [ ! -f "${WORKSPACE}/venv/bin/activate" ]; then
  echo -e "\nCreating virtualenv...\n"
  /usr/bin/virtualenv -q ${WORKSPACE}/venv
  source ${WORKSPACE}/venv/bin/activate
  pip install -U pip setuptools && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple docker-compose && \
  pip install --trusted-host pypi -i http://pypi/nexus/repository/pypi-all/simple rp-retry && \
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

check_arsenal_ready

cd ${CLIENT_DIR}
python2.7 setup.py develop
./bin/client_test.sh -s ${ARSENAL_SERVER}

cd ${REGRESSION_DIR}/docker
echo -e '\nShutting down docker images...\n'
docker-compose down
echo -e '\ndocker images shut down.\n'.
