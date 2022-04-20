'''Arsenal API Tags.'''
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
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import DatabaseError
from arsenalweb.models.data_centers import (
    DataCenter,
    DataCenterAudit,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.models.node_groups import (
    NodeGroup,
    NodeGroupAudit,
    )
from arsenalweb.models.physical_devices import (
    PhysicalDevice,
    PhysicalDeviceAudit,
    )
from arsenalweb.models.tags import (
    Tag,
    TagAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_403,
    api_404,
    api_409,
    api_500,
    api_501,
    underscore_to_camel,
    validate_tag_perm,
    )
from arsenalweb.views.api.data_centers import (
    find_data_center_by_id,
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )
from arsenalweb.views.api.node_groups import (
    find_node_group_by_id,
    )
from arsenalweb.views.api.physical_devices import (
    find_physical_device_by_id,
    )

LOG = logging.getLogger(__name__)

# Functions
def find_tag_by_name(dbsession, name, value):
    '''Search for an existing tag by name and value.'''

    LOG.debug('Searching for tag name: %s value: %s', name, value)
    try:
        tag = dbsession.query(Tag)
        tag = tag.filter(Tag.name == name)
        tag = tag.filter(Tag.value == value)
        one = tag.one()
    except DatabaseError:
        tag = dbsession.query(Tag)
        tag = tag.filter(Tag.name == name)
        tag = tag.filter(Tag.value == str(value))
        one = tag.one()
    return one

def find_tag_by_id(dbsession, tag_id):
    '''Search for an existing tag by id.'''

    LOG.debug('Searching for tag id: %s', tag_id)
    tag = dbsession.query(Tag)
    tag = tag.filter(Tag.id == tag_id)
    return tag.one()

def create_tag(dbsession, name, value, user):
    '''Create a new tag.'''

    try:
        LOG.info('Creating new tag name: %s value: %s', name, value)
        utcnow = datetime.utcnow()

        tag = Tag(name=name,
                  value=value,
                  updated_by=user,
                  created=utcnow,
                  updated=utcnow)

        dbsession.add(tag)
        dbsession.flush()
        tag_audit = TagAudit(object_id=tag.id,
                             field='tag_id',
                             old_value='created',
                             new_value='{0}={1}'.format(tag.name, tag.value),
                             updated_by=user,
                             created=utcnow)
        dbsession.add(tag_audit)
        dbsession.flush()

        return api_200(results=tag)

    except Exception as ex:
        msg = 'Error creating new tag name: {0} value: {1},' \
              'exception: {2}'.format(name, value, ex)
        LOG.error(msg)
        return api_500(msg=msg)

def manage_tags(dbsession, tag, tagable_type, tagables, action, user):
    '''Manage tag assignment/deassignments to a list of id's. Takes a list of
    ids and assigns them to the tag. Assigning a tag to a node also removes any
    other tag(s) with the same key.

    tag     : A Tag object.
    tagable_type: The type of object you are tagging. One of nodes, node_groups
        or data_centers.
    tagables: A list of node, node_group, data_center, or physical_device id's to
        assign/deassign the tag to/from.
    action  : A string representing the action to perform. One of either 'PUT' or 'DELETE'.
    '''

    valid_types = [
        'nodes',
        'node_groups',
        'data_centers',
        'physical_devices',
    ]
    if tagable_type not in valid_types:
        msg = 'Invalid tagable type: {0}'.format(tagable_type)
        LOG.error(msg)
        raise NotImplementedError(msg)

    find_by_id = globals()['find_{0}_by_id'.format(tagable_type[:-1])]
    create_audit = globals()['{0}Audit'.format(underscore_to_camel(tagable_type[:-1]))]
    LOG.debug('Find by id function: %s', find_by_id)

    try:
        tag_kv = '{0}={1}'.format(tag.name, tag.value)
        resp = {tag_kv: []}
        for tagable_id in tagables:
            tagable = find_by_id(dbsession, tagable_id)

            try:
                resp[tag_kv].append(tagable.name)
            except AttributeError:
                LOG.debug('This object has no name, using serial_number instead.')
                resp[tag_kv].append(tagable.serial_number)

            current_tags_list = [my_tag.id for my_tag in tagable.tags]
            current_tags_remove = [my_tag.id for my_tag in tagable.tags if
                                   my_tag.name == tag.name and my_tag.value
                                   != tag.value]
            utcnow = datetime.utcnow()

            if action == 'PUT':
                if tag.id not in current_tags_list:
                    my_audit = create_audit(object_id=tagable.id,
                                            field='tag',
                                            old_value='assigned',
                                            new_value='{0}={1}'.format(tag.name,
                                                                       tag.value),
                                            updated_by=user,
                                            created=utcnow)
                    dbsession.add(my_audit)
                    my_subtype = getattr(tag, tagable_type)
                    my_subtype.append(tagable)
                # Ensure only one tag key is present on a tagable object.
                for remove_id in current_tags_remove:
                    remove_tag = find_tag_by_id(dbsession, remove_id)
                    LOG.debug('De-assigning tag from %s for uniqueness. name: '
                              '%s value: %s', tagable_type,
                                              remove_tag.name,
                                              remove_tag.value)
                    my_subtype = getattr(remove_tag, tagable_type)
                    my_subtype.remove(tagable)
                    my_audit = create_audit(object_id=tagable.id,
                                            field='tag',
                                            old_value='{0}={1}'.format(remove_tag.name,
                                                                       remove_tag.value),
                                            new_value='de-assigned',
                                            updated_by=user,
                                            created=utcnow)
                    dbsession.add(remove_tag)
                    dbsession.add(my_audit)

            if action == 'DELETE':
                try:
                    my_subtype = getattr(tag, tagable_type)
                    if tagable in my_subtype:
                        my_subtype.remove(tagable)
                    my_audit = create_audit(object_id=tagable.id,
                                            field='tag',
                                            old_value='{0}={1}'.format(tag.name,
                                                                       tag.value),
                                            new_value='de-assigned',
                                            updated_by=user,
                                            created=utcnow)
                    dbsession.add(my_audit)
                except ValueError:
                    pass

        dbsession.add(tag)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node not found')

    except MultipleResultsFound:
        msg = 'Bad request: {0}_id is not unique: {1}'.format(tagable_type, tagable_id)
        return api_400(msg=msg)
    except Exception as ex:
        msg = 'Error updating FLUBBER: exception={0}'.format(type(ex))
        LOG.error(msg)
        return api_500(msg)

    return api_200(results=resp)

# Routes
@view_config(route_name='api_tags', request_method='GET', request_param='schema=true', renderer='json')
def api_tag_schema(request):
    '''Schema document for tags API'''

    tag = {
    }

    return tag

@view_config(route_name='api_tags', permission='tag_write', request_method='PUT', renderer='json', require_csrf=False)
def api_tags_write(request):
    '''Process write requests for the /api/tags route.'''

    try:
        user = request.identity
        payload = request.json_body
        tag_name = payload['name'].rstrip()
        tag_value = payload['value'].rstrip()
        try:
            if tag_value != '0':
                tag_value = int(tag_value)
        except ValueError:
            pass

        LOG.info('Searching for tag name: %s', tag_name)

        try:
            tag = find_tag_by_name(request.dbsession, tag_name, tag_value)
            # Since there are no fields to update other than the two that
            # constitue a unqiue tag we return a 409 when an update would
            # have otherwise happened and handle it in client/UI.
            return api_409()
        except NoResultFound:
            # FIXME: THis is probably broken due to user
            if validate_tag_perm(request, user, tag_name):
                tag = create_tag(request.dbsession, tag_name, tag_value, user['name'])
            else:
                return api_403()
        return tag

    except Exception as ex:
        msg = 'Error writing to tags API={0},exception={1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_tag_r', permission='tag_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_tag_r', permission='tag_write', request_method='PUT', renderer='json', require_csrf=False)
def api_tag_write_attrib(request):
    '''Process write requests for the /api/tags/{id}/{resource} route.'''

    try:
        resource = request.matchdict['resource']
        payload = request.json_body
        user = request.identity

        LOG.debug('Processing update for route: %s', request.url)

        # First get the tag, then figure out what to do to it.
        tag = find_tag_by_id(request.dbsession, request.matchdict['id'])
        LOG.debug('tag is: %s', tag)

        # List of resources allowed
        resources = [
            'data_centers',
            'node_groups',
            'nodes',
            'physical_devices',
        ]

        if resource in resources:
            try:
                actionable = payload[resource]

                # FIXME: THis is probably broken due to user
                if validate_tag_perm(request, user, tag.name):
                    resp = manage_tags(request.dbsession,
                                       tag,
                                       resource,
                                       payload[resource],
                                       request.method,
                                       user['name'])
                else:
                    return api_403()
            except KeyError as ex:
                msg = 'Missing required parameter: {0} execption: ' \
                      '{1}'.format(resource, repr(ex))
                LOG.debug(msg)
                return api_400(msg=msg)
            except Exception as ex:
                LOG.error('Error updating tags: %s exception: %s', request.url, ex)
                return api_500(msg=str(ex))
        else:
            return api_501()

        return resp
    except Exception as ex:
        LOG.error('Error updating tags: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))
