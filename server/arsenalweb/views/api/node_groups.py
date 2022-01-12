'''Arsenal API node_groups.'''
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
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.models.node_groups import (
    NodeGroup,
    NodeGroupAudit,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    api_501,
    enforce_api_change_limit,
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )

LOG = logging.getLogger(__name__)


# Functions
def find_node_group_by_name(dbsession, name):
    '''Find a node_group by name.'''

    node_group = dbsession.query(NodeGroup)
    node_group = node_group.filter(NodeGroup.name == name)

    return node_group.one()

def find_node_group_by_id(dbsession, node_group_id):
    '''Find a node_group by id.'''

    node_group = dbsession.query(NodeGroup)
    node_group = node_group.filter(NodeGroup.id == node_group_id)

    return node_group.one()

def create_node_group(dbsession, name, owner, description, notes_url, user):
    '''Create a new node_group.'''

    try:
        LOG.info('Creating new node_group name: %s owner: %s '
                 'description: %s notes_url: %s', name,
                                                  owner,
                                                  description,
                                                  notes_url)
        utcnow = datetime.utcnow()

        node_group = NodeGroup(name=name,
                               owner=owner,
                               description=description,
                               notes_url=notes_url,
                               updated_by=user,
                               created=utcnow,
                               updated=utcnow)

        dbsession.add(node_group)
        dbsession.flush()

        audit = NodeGroupAudit(object_id=node_group.id,
                               field='name',
                               old_value='created',
                               new_value=node_group.name,
                               updated_by=user,
                               created=utcnow)
        dbsession.add(audit)
        dbsession.flush()

        return node_group

    except Exception as ex:
        msg = 'Error creating new node_group name: {0} owner: {1} ' \
                'description: {2} notes_url: {3} exception: {4}'.format(name,
                                                                        owner,
                                                                        description,
                                                                        notes_url,
                                                                        ex)
        LOG.error(msg)
        return api_500(msg=msg)

def nodes_to_node_groups(dbsession, node_group, nodes, action, user):
    '''Manage node_group assignment/deassignments. Takes a list of node
       ids and assigns/deassigns them to/from the node group.'''

    resp = {node_group.name: []}
    try:
        for node_id in nodes:
            node = find_node_by_id(dbsession, node_id)
            resp[node_group.name].append(node.name)

            utcnow = datetime.utcnow()

            if action == 'PUT':
                if not node in node_group.nodes:
                    node_group.nodes.append(node)
                    audit = NodeAudit(object_id=node.id,
                                      field='node_group',
                                      old_value='assigned',
                                      new_value=node_group.name,
                                      updated_by=user['name'],
                                      created=utcnow)
                    dbsession.add(audit)
            if action == 'DELETE':
                try:
                    node_group.nodes.remove(node)
                    audit = NodeAudit(object_id=node.id,
                                      field='node_group',
                                      old_value=node_group.name,
                                      new_value='deassigned',
                                      updated_by=user['name'],
                                      created=utcnow)
                    dbsession.add(audit)
                except (ValueError, AttributeError):
                    try:
                        dbsession.remove(audit)
                    except  UnboundLocalError:
                        pass

        dbsession.add(node_group)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node not found')

    except MultipleResultsFound:
        msg = 'Bad request: node_id is not unique: {0}'.format(node_id)
        return api_400(msg=msg)
    except Exception as ex:
        msg = 'Error updating node: exception={0}'.format(ex)
        LOG.error(msg)
        return api_500(msg=msg)

    return resp

# Routes
@view_config(route_name='api_node_groups', request_method='GET', request_param='schema=true', renderer='json')
def api_node_groups_schema(request):
    '''Schema document for the node_groups API.'''

    node_groups = {
    }

    return node_groups

@view_config(route_name='api_node_groups', permission='node_group_write', request_method='PUT', renderer='json', require_csrf=False)
def api_node_groups_write(request):
    '''Process write requests for /api/node_groups route.'''

    try:
        user = request.identity
        payload = request.json_body

        name = payload['name'].rstrip()
        owner = payload['owner'].rstrip()
        description = payload['description'].rstrip()
        try:
            notes_url = payload['notes_url'].rstrip()
        except:
            notes_url = None

        LOG.debug('Searching for node_group name: %s', name)

        try:
            node_group = find_node_group_by_name(request.dbsession, name)
            try:
                LOG.info('Updating node_group name: %s', name)

                utcnow = datetime.utcnow()

                for attribute in ['name', 'owner', 'description', 'notes_url']:
                    if getattr(node_group, attribute) != locals()[attribute]:
                        LOG.debug('Updating node group %s: %s', attribute, locals()[attribute])
                        old_value = getattr(node_group, attribute)
                        if not old_value:
                            old_value = 'None'
                        node_group_audit = NodeGroupAudit(object_id=node_group.id,
                                                          field=attribute,
                                                          old_value=old_value,
                                                          new_value=locals()[attribute],
                                                          updated_by=user['name'],
                                                          created=utcnow)
                        request.dbsession.add(node_group_audit)

                node_group.name = name
                node_group.owner = owner
                node_group.description = description
                node_group.notes_url = notes_url
                node_group.updated_by = user['name']

                request.dbsession.flush()

            except Exception as ex:
                msg = 'Error updating node_group name: {0} owner: {1} ' \
                      'description: {2} notes_url: {3} exception: {4}'.format(name,
                                                                              owner,
                                                                              description,
                                                                              notes_url,
                                                                              ex)

                LOG.error(msg)
                return api_500(msg=msg)

        except NoResultFound:
            node_group = create_node_group(request.dbsession,
                                           name,
                                           owner,
                                           description,
                                           notes_url,
                                           user['name'])

        return api_200(results=node_group)

    except Exception as ex:
        msg = 'Error writing to node_groups API: {0} exception: {1}'.format(request.url, ex)
        LOG.error(msg)
        return api_500(msg=msg)

@view_config(route_name='api_node_group_r', permission='node_group_delete', request_method='DELETE', renderer='json', require_csrf=False)
@view_config(route_name='api_node_group_r', permission='node_group_write', request_method='PUT', renderer='json', require_csrf=False)
def api_node_group_write_attrib(request):
    '''Process write requests for the /api/node_groups/{id}/{resource} route.'''

    resource = request.matchdict['resource']
    payload = request.json_body
    user = request.identity

    LOG.debug('Updating %s', request.url)

    # First get the node_group, then figure out what to do to it.
    node_group = find_node_group_by_id(request.dbsession, request.matchdict['id'])
    LOG.debug('node_group is: %s', node_group)

    # List of resources allowed
    resources = [
        'nodes',
        'tags',
    ]

    if resource in resources:
        try:
            actionable = payload[resource]

            item_count = len(actionable)
            denied = enforce_api_change_limit(request, item_count)
            if denied:
                return api_400(msg=denied)

            if resource == 'tags':
                # FIXME: This is missing, is it needed?
                resp = manage_tags(request.dbsession, node_group, actionable, request.method)
            if resource == 'nodes':
                resp = nodes_to_node_groups(request.dbsession,
                                            node_group,
                                            actionable,
                                            request.method,
                                            user)
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(resource)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error updating node_groups: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))
    else:
        return api_501()

    return api_200(results=resp)
