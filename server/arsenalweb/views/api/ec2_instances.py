'''Arsenal API ec2_instance.'''
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
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views.api.common import (
    api_500,
    collect_params,
    )
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.ec2_instances import (
    Ec2Instance,
    Ec2InstanceAudit,
    )

LOG = logging.getLogger(__name__)


def find_ec2_instance_by_id(instance_id):
    '''Find an ec2_instance by it's instance_id. Returns an ec2_instance if found,
    raises NoResultFound otherwise.'''

    LOG.debug('Searching for ec2_instance by instance_id: {0}'.format(instance_id))
    ec2 = DBSession.query(Ec2Instance)
    ec2 = ec2.filter(Ec2Instance.instance_id == instance_id)
    return ec2.one()

def create_ec2_instance(instance_id=None, updated_by=None, **kwargs):
    '''Create a new ec2_instance.

    Required params:

    instance_id: A string that is the ec2 instance ID.
    updated_by : A string that is the user making the update.

    Optional kwargs:

    ami_id           : A string that is the ami_id.
    hostname         : A string that is the hostname.
    instance_id      : A string that is the instance_id.
    instance_type    : A string that is the instance_type.
    availability_zone: A string that is the availability_zone.
    profile          : A string that is the profile.
    reservation_id   : A string that is the reservation_id.
    security_groups  : A string that is the security_groups.
    '''

    try:
        LOG.info('Creating new ec2_instance id: {0}'.format(instance_id))

        utcnow = datetime.utcnow()

        ec2 = Ec2Instance(instance_id=instance_id,
                          updated_by=updated_by,
                          created=utcnow,
                          updated=utcnow,
                          **kwargs)

        DBSession.add(ec2)
        DBSession.flush()

        audit = Ec2InstanceAudit(object_id=ec2.id,
                                 field='instance_id',
                                 old_value='created',
                                 new_value=ec2.instance_id,
                                 updated_by=updated_by,
                                 created=utcnow)
        DBSession.add(audit)
        DBSession.flush()

        return ec2
    except Exception as ex:
        msg = 'Error creating new ec2_instance id: {0} ' \
              'exception: {1}'.format(instance_id, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def update_ec2_instance(ec2, **kwargs):
    '''Update an existing ec2_instance.

    Required params:

    ec2: The existing ec2 object to update.
    updated_by : A string that is the user making the update.

    Optional kwargs:

    ami_id           : A string that is the ami_id.
    hostname         : A string that is the hostname.
    instance_type    : A string that is the instance_type.
    availability_zone: A string that is the availability_zone.
    profile          : A string that is the profile.
    reservation_id   : A string that is the reservation_id.
    security_groups  : A string that is the security_groups.
    '''

    try:
        # Convert everything that is defined to a string.
        my_attribs = kwargs.copy()
        for my_attr in my_attribs:
            if my_attribs.get(my_attr):
                my_attribs[my_attr] = str(my_attribs[my_attr])

        LOG.info('Updating ec2_instance ec2_instance_id={0}'.format(ec2.instance_id))

        utcnow = datetime.utcnow()

        for attribute in my_attribs:
            if attribute == 'instance_id':
                LOG.debug('Skipping update to ec2.instance_id.')
                continue
            old_value = getattr(ec2, attribute)
            new_value = my_attribs[attribute]

            if old_value != new_value and new_value:
                if not old_value:
                    old_value = 'None'

                LOG.debug('Updating ec2_instance: {0} attribute: '
                          '{1} new_value: {2}'.format(ec2.instance_id,
                                                      attribute,
                                                      new_value))
                audit = Ec2InstanceAudit(object_id=ec2.id,
                                         field=attribute,
                                         old_value=old_value,
                                         new_value=new_value,
                                         updated_by=my_attribs['updated_by'],
                                         created=utcnow)
                DBSession.add(audit)
                setattr(ec2, attribute, new_value)

        DBSession.flush()

        return ec2

    except Exception as ex:
        LOG.error('Error updating ec2_instance instance_id={0},'
                  'exception={1}'.format(ec2.instance_id, repr(ex)))
        raise

@view_config(route_name='api_ec2_instances', request_method='GET', request_param='schema=true', renderer='json')
def api_ec2_instances_schema(request):
    '''Schema document for the ec2_instances API.'''

    ec2 = {
    }

    return ec2

@view_config(route_name='api_ec2_instances', permission='api_write', request_method='PUT', renderer='json')
def api_ec2_instance_write(request):
    '''Process write requests for /api/ec2_instances route.'''

    try:
        req_params = [
            'instance_id',
        ]
        opt_params = [
            'ami_id',
            'availability_zone',
            'hostname',
            'instance_type',
            'profile',
            'reservation_id',
            'security_groups',
        ]
        params = collect_params(request, req_params, opt_params)

        LOG.debug('Searching for ec2_instance id: {0}'.format(params['instance_id']))

        try:
            ec2 = find_ec2_instance_by_id(params['instance_id'])
            ec2 = update_ec2_instance(ec2, **params)
        except NoResultFound:
            ec2 = create_ec2_instance(**params)

        return ec2

    except Exception as ex:
        msg = 'Error writing to ec2_instances API: {0} exception: {1}'.format(request.url, repr(ex))
        LOG.error(msg)
        return api_500(msg=msg)
