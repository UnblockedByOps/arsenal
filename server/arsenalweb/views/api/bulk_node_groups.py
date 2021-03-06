'''Arsenal API bulk node_groups.'''
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
from arsenalweb.models.common import (
    DBSession,
    )
from arsenalweb.models.nodes import (
    NodeAudit,
    )
from arsenalweb.views import (
    get_authenticated_user,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_404,
    api_500,
    )
from arsenalweb.views.api.nodes import (
    find_node_by_id,
    )

LOG = logging.getLogger(__name__)

def remove_node_groups(node_ids, auth_user):
    '''Remove all node_groups from a list of node_ids.'''

    resp = {'nodes': []}
    try:
        for node_id in node_ids:

            node = find_node_by_id(node_id)
            LOG.debug('Removing all node_groups from node: {0} '
                      'node_groups: {1}'.format(node.name,
                                                [ng.name for ng in node.node_groups]))
            resp['nodes'].append(node.name)
            utcnow = datetime.utcnow()

            LOG.debug('node_group objects: {0}'.format(node.node_groups))
            for node_group in list(node.node_groups):
                LOG.debug('Removing node_group: {0}'.format(node_group.name))
                try:
                    audit = NodeAudit(object_id=node.id,
                                      field='node_group',
                                      old_value=node_group.name,
                                      new_value='deleted',
                                      updated_by=auth_user['user_id'],
                                      created=utcnow)
                    DBSession.add(audit)
                    LOG.debug('Trying to remove node_group: {0} from '
                              'node: {1}'.format(node_group.name, node.name,))
                    node.node_groups.remove(node_group)
                    LOG.debug('Successfully removed node_group: {0} from '
                              'node: {1}'.format(node_group.name, node.name,))
                except (ValueError, AttributeError) as ex:
                    LOG.debug('Died removing node_group: {0}'.format(ex))
                    DBSession.remove(audit)
                except Exception as ex:
                    LOG.debug('Died removing node_group: {0}'.format(ex))
                    DBSession.remove(audit)

            LOG.debug('Final node_groups: {0}'.format([ng.name for ng in node.node_groups]))
            DBSession.add(node)
        DBSession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='node_group not found')
    except MultipleResultsFound:
        msg = 'Bad request: node_id is not unique: {0}'.format(node_id)
        return api_400(msg=msg)
    except Exception as ex:
        LOG.error('Error removing all node_groups from node. exception={0}'.format(ex))
        return api_500()

    return resp

@view_config(route_name='api_b_node_groups_deassign', permission='node_group_delete', request_method='DELETE', renderer='json')
def api_b_node_groups_deassign(request):
    '''Process delete requests for the /api/bulk/node_groups/deassign route.
    Takes a list of nodes and deassigns all node_groups from them.'''

    try:
        payload = request.json_body
        node_ids = payload['node_ids']
        auth_user = get_authenticated_user(request)

        LOG.debug('Updating {0}'.format(request.url))

        try:
            resp = remove_node_groups(node_ids, auth_user)
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(payload)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error removing all node_groups from '
                      'node={0},exception={1}'.format(request.url, ex))
            return api_500(msg=str(ex))

        return api_200(results=resp)

    except Exception as ex:
        LOG.error('Error updating node_groups={0},exception={1}'.format(request.url, ex))
        return api_500(msg=str(ex))
