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
from pyramid.view import view_config
from pyramid.response import Response
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    log,
    get_pag_params,
    )
from arsenalweb.views.api import (
    get_api_attribute,
    api_read_by_id,
    api_read_by_params,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    Ec2,
    )


def create_ec2_object(ec2_instance_id,
               ec2_ami_id,
               ec2_hostname,
               ec2_public_hostname,
               ec2_instance_type,
               ec2_security_groups,
               ec2_placement_availability_zone,
               user_id):
    """
    Create a new ec2 object.
    """

    try:
        log.info('Creating new ec2 ec2_instance_id={0}'.format(ec2_instance_id))
        utcnow = datetime.utcnow()

        ec2 = Ec2(ec2_instance_id = ec2_instance_id,
                  ec2_ami_id = ec2_ami_id,
                  ec2_hostname = ec2_hostname,
                  ec2_public_hostname = ec2_public_hostname,
                  ec2_instance_type = ec2_instance_type,
                  ec2_security_groups = ec2_security_groups,
                  ec2_placement_availability_zone = ec2_placement_availability_zone,
                  updated_by = user_id,
                  created = utcnow,
                  updated = utcnow)

        DBSession.add(ec2)
        DBSession.flush()
        return ec2
    except Exception as e:
        log.error('Error creating new ec2 ec2_instance_id={0},exception={1}'.format(ec2_instance_id,e))
        raise


@view_config(route_name='api_ec2_objects', request_method='GET', request_param='schema=true', renderer='json')
def api_ec2_objects_schema(request):
    """Schema document for the ec2_objects API."""

    ec2 = {
    }

    return ec2


@view_config(route_name='api_ec2_object_r', request_method='GET', renderer='json')
def api_ec2_object_read_attrib(request):
    """Process read requests for the /api/ec2_objects/{id}/{resource} route."""

    return get_api_attribute(request, 'Ec2')


@view_config(route_name='api_ec2_object', request_method='GET', renderer='json')
def api_ec2_object_read_id(request):
    """Process read requests for the /api/node_groups/{id} route."""

    return api_read_by_id(request, 'HardwareProfile')


@view_config(route_name='api_ec2_objects', request_method='GET', renderer='json')
def api_ec2_object_read(request):
    """Process read requests for the /api/ec2_objects route."""

    return api_read_by_params(request, 'Ec2')


@view_config(route_name='api_ec2_objects', permission='api_write', request_method='PUT', renderer='json')
def api_ec2_object_write(request):
    """Process write requests for /api/ec2_objects route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        ec2_instance_id = payload['ec2_instance_id']
        ec2_ami_id = payload['ec2_ami_id']
        ec2_hostname = payload['ec2_hostname']
        ec2_public_hostname = payload['ec2_public_hostname']
        ec2_instance_type = payload['ec2_instance_type']
        ec2_security_groups = payload['ec2_security_groups']
        ec2_placement_availability_zone = payload['ec2_placement_availability_zone']

        log.debug('Checking for ec2_object ec2_instance_id={0}'.format(ec2_instance_id))

        try:
            ec2 = DBSession.query(Ec2)
            ec2 = ec2.filter(Ec2.ec2_instance_id==ec2_instance_id)
            ec2 = ec2.one()
        except NoResultFound:
            ec2 = create_ec2_object(ec2_instance_id,
                                    ec2_ami_id,
                                    ec2_hostname,
                                    ec2_public_hostname,
                                    ec2_instance_type,
                                    ec2_security_groups,
                                    ec2_placement_availability_zone,
                                    au['user_id'])
        else:
            try:
                log.info('Updating ec2_object ec2_instance_id={0}'.format(ec2_instance_id))

                ec2.ec2_ami_id = ec2_ami_id
                ec2.ec2_hostname = ec2_hostname
                ec2.ec2_public_hostname = ec2_public_hostname
                ec2.ec2_instance_type = ec2_instance_type
                ec2.ec2_security_groups = ec2_security_groups
                ec2.ec2_placement_availability_zone = ec2_placement_availability_zone
                ec2.updated_by=au['user_id']

                DBSession.flush()
            except Exception as e:
                log.error('Error updating ec2_object ec2_instance_id={0}'.format(ec2_instance_id, e))
                raise

        return ec2

    except Exception as e:
        log.error('Error writing to ec2_objects API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_ec2_object', permission='api_write', request_method='DELETE', renderer='json')
def api_ec2_objects_delete_id(request):
    """Process delete requests for the /api/ec2_objects/{id} route."""

    return api_delete_by_id(request, 'Ec2')


@view_config(route_name='api_ec2_objects', permission='api_write', request_method='DELETE', renderer='json')
def api_ec2_objects_delete(request):
    """Process delete requests for the /api/ec2_objects route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'Ec2')


