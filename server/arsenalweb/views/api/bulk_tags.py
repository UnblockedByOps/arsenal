'''Arsenal API bulk tags.'''
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

def remove_tags(dbsession, node_ids, user):
    '''Remove all tags from a list of node_ids.'''

    resp = {'nodes': []}
    try:
        for node_id in node_ids:

            node = find_node_by_id(dbsession, node_id)
            LOG.debug('Removing all tags from node: %s '
                      'tags: %s', node.name, [ng.name for ng in node.tags])
            resp['nodes'].append(node.name)
            utcnow = datetime.utcnow()

            LOG.debug('tag objects: %s', node.tags)
            for tag in list(node.tags):
                LOG.debug('Removing tag: %s=%s', tag.name, tag.value)
                try:
                    audit = NodeAudit(object_id=node.id,
                                      field='tag',
                                      old_value='{0}={1}'.format(tag.name, tag.value),
                                      new_value='deleted',
                                      updated_by=user['name'],
                                      created=utcnow)
                    dbsession.add(audit)
                    LOG.debug('Trying to remove tag: %s=%s from '
                              'node: %s', tag.name, tag.value, node.name)
                    node.tags.remove(tag)
                    LOG.debug('Successfully removed tag: %s=%s from '
                              'node: %s', tag.name, tag.value, node.name)
                except (ValueError, AttributeError) as ex:
                    LOG.debug('Died removing tag: %s', ex)
                    dbsession.remove(audit)
                except Exception as ex:
                    LOG.debug('Died removing tag: %s', ex)
                    dbsession.remove(audit)

            LOG.debug('Final tags: %s', [tag.name for tag in node.tags])
            dbsession.add(node)
        dbsession.flush()

    except (NoResultFound, AttributeError):
        return api_404(msg='tag not found')
    except MultipleResultsFound:
        msg = 'Bad request: node_id is not unique: {0}'.format(node_id)
        return api_400(msg=msg)
    except Exception as ex:
        LOG.error('Error removing all tags from node. exception: %s', ex)
        return api_500()

    return resp

@view_config(route_name='api_b_tags_deassign', permission='tag_delete', request_method='DELETE', renderer='json', require_csrf=False)
def api_b_tagss_deassign(request):
    '''Process delete requests for the /api/bulk/tags/deassign route.
    Takes a list of nodes and deassigns all tags from them.'''

    try:
        payload = request.json_body
        node_ids = payload['node_ids']
        user = request.identity

        LOG.debug('Updating %s', request.url)

        try:
            resp = remove_tags(request.dbsession, node_ids, user)
        except KeyError:
            msg = 'Missing required parameter: {0}'.format(payload)
            return api_400(msg=msg)
        except Exception as ex:
            LOG.error('Error removing all tags from '
                      'node: %s exception: %s', request.url, ex)
            return api_500(msg=str(ex))

        return api_200(results=resp)

    except Exception as ex:
        LOG.error('Error updating tags: %s exception: %s', request.url, ex)
        return api_500(msg=str(ex))
