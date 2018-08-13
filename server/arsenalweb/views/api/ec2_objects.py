'''Arsenal API ec2_object.'''
#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import logging
from datetime import datetime
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    )
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.ec2 import (
    Ec2,
    )

LOG = logging.getLogger(__name__)


def get_ec2_object(instance_id):
    '''Get an ec2 object from the databasse. Returns an ec2 object if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for ec2 instance by instance_id: {0}'.format(instance_id))
    ec2 = DBSession.query(Ec2)
    ec2 = ec2.filter(Ec2.instance_id == instance_id)
    return ec2.one()

def create_ec2_object(instance_id,
                      ami_id,
                      hostname,
                      public_hostname,
                      instance_type,
                      security_groups,
                      placement_availability_zone,
                      user_id):
    '''Create a new ec2 object.'''

    try:
        LOG.info('Creating new ec2 instance_id={0}'.format(instance_id))
        utcnow = datetime.utcnow()

        ec2 = Ec2(instance_id=instance_id,
                  ami_id=ami_id,
                  hostname=hostname,
                  public_hostname=public_hostname,
                  instance_type=instance_type,
                  security_groups=security_groups,
                  placement_availability_zone=placement_availability_zone,
                  updated_by=user_id,
                  created=utcnow,
                  updated=utcnow)

        DBSession.add(ec2)
        DBSession.flush()

        return ec2

    except Exception as ex:
        LOG.error('Error creating new ec2 instance_id={0},'
                  'exception={1}'.format(instance_id, ex))
        raise

def update_ec2_object(ec2,
                      instance_id,
                      ami_id,
                      hostname,
                      public_hostname,
                      instance_type,
                      security_groups,
                      placement_availability_zone,
                      user_id):
    '''Update an existing ec2 object.'''

    try:
        LOG.info('Updating ec2_object ec2_instance_id={0}'.format(instance_id))

        ec2.ami_id = ami_id
        ec2.hostname = hostname
        ec2.public_hostname = public_hostname
        ec2.instance_type = instance_type
        ec2.security_groups = security_groups
        ec2.placement_availability_zone = placement_availability_zone
        ec2.updated_by = user_id

        DBSession.flush()

        return ec2

    except Exception as ex:
        LOG.error('Error updating ec2_object instance_id={0},'
                  'exception={1}'.format(instance_id, ex))
        raise

@view_config(route_name='api_ec2_objects', request_method='GET', request_param='schema=true', renderer='json')
def api_ec2_objects_schema(request):
    '''Schema document for the ec2_objects API.'''

    ec2 = {
    }

    return ec2

@view_config(route_name='api_ec2_objects', permission='api_write', request_method='PUT', renderer='json')
def api_ec2_object_write(request):
    '''Process write requests for /api/ec2_objects route.'''

    try:
        auth_user = get_authenticated_user(request)
        payload = request.json_body
        instance_id = payload['instance_id'].rstrip()
        ami_id = payload['ami_id'].rstrip()
        hostname = payload['hostname'].rstrip()
        public_hostname = payload['public_hostname'].rstrip()
        instance_type = payload['instance_type'].rstrip()
        security_groups = payload['security_groups'].rstrip()
        placement_availability_zone = payload['placement_availability_zone'].rstrip()

        ec2 = get_ec2_object(instance_id)

        if not ec2:
            ec2 = create_ec2_object(instance_id,
                                    ami_id,
                                    hostname,
                                    public_hostname,
                                    instance_type,
                                    security_groups,
                                    placement_availability_zone,
                                    auth_user['user_id'])
        else:
            ec2 = update_ec2_object(ec2,
                                    instance_id,
                                    ami_id,
                                    hostname,
                                    public_hostname,
                                    instance_type,
                                    security_groups,
                                    placement_availability_zone,
                                    auth_user['user_id'])

        return ec2

    except Exception as ex:
        LOG.error('Error writing to ec2_objects API={0},exception={1}'.format(request.url, ex))
        return Response(str(ex), content_type='text/plain', status_int=500)
