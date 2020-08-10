'''Arsenal API ENC for puppet.'''
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
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.models.common import (
    DBSession,
)
from arsenalweb.models.nodes import (
    Node,
    )
from arsenalweb.views.api.common import (
    api_200,
    api_400,
    api_500,
    api_501,
    )

LOG = logging.getLogger(__name__)

def find_node_by_name_and_status(settings, node_name):
    '''Find a node by name, filtered by statuses'''

    try:
        status_ids = [s for s in settings['arsenal.enc.status_ids'].splitlines() if s]
    except KeyError as ex:
        msg = 'You must define arsenal.enc.status_ids in the main settings file to ' \
              'enable the enc.'
        LOG.error(msg)
        raise type(ex)(ex.message + ' {0}'.format(msg))

    node = DBSession.query(Node)
    node = node.filter(Node.name == node_name)
    node = node.filter(Node.status_id.in_(status_ids))

    return node.one()

def process_tags(tags, tag_type):
    '''Processes tags. If the value is 'True' or 'False', converts it to a
    boolean. Otherwise returns as-is (what about integers?).'''

    results = {}
    for tag in tags:
        LOG.debug('{0} tag: {1}={2}'.format(tag_type, tag.name, tag.value))
        if tag.value == 'True':
            results[tag.name] = bool(tag.value)
        elif tag.value == 'False':
            results[tag.name] = bool('')
        else:
            try:
                my_value = tag.value
                my_value = int(my_value)
            except ValueError:
                pass
            results[tag.name] = my_value

    return results

def process_node_enc(settings, node_name, param_sources=False):
    '''Process enc for node. Merges tags from the following three
    objects in order from least to most specific:

        node_group
        data_center
        node

    Multiple node groups are sorted and take priority..?'''

    results = {}
    results['classes'] = []
    results['parameters'] = {}
    results['status'] = {
        'name': None,
    }
    if param_sources:
        results['param_sources'] = {}

    try:
        LOG.debug('ENC find the node...')
        node = find_node_by_name_and_status(settings, node_name)
        LOG.debug('ENC find the node complete')
        results['name'] = node.name
        results['id'] = node.id
        results['status'] = node.status

        LOG.debug('ENC node name is: {0}'.format(node.name))
        LOG.debug('ENC node datacenter is: {0}'.format(node.data_center_id))

        # What happens when there's more than one node group? What tags
        # win, alphabetic?
        LOG.debug('ENC find node_group tags...')
        for node_group in node.node_groups:
            LOG.debug('ENC node_group: {0}'.format(node_group.name))
            results['classes'].append(node_group.name)
            my_tags = process_tags(node_group.tags, 'node_group')
            results['parameters'].update(my_tags)
            if param_sources:
                for tag in my_tags:
                    results['param_sources'][tag] = 'node_group'
        LOG.debug('ENC find node_group tags complete.')

        LOG.debug('ENC process data_center tags...')
        try:
            my_tags = process_tags(node.data_center.tags, 'data_center')
        except AttributeError:
            my_tags = {}

        LOG.debug('ENC process data_center tags complete.')
        results['parameters'].update(my_tags)
        if param_sources:
            for tag in my_tags:
                results['param_sources'][tag] = 'data_center'

        LOG.debug('ENC process node tags...')
        my_tags = process_tags(node.tags, 'node')
        results['parameters'].update(my_tags)
        if param_sources:
            for tag in my_tags:
                results['param_sources'][tag] = 'node'

        LOG.debug('ENC process node tags complete.')

    except NoResultFound:
        LOG.debug('node not found: {0}'.format(node_name))
    except (AttributeError, KeyError):
        raise

    return results

@view_config(route_name='api_enc', request_method='GET', renderer='json')
def api_enc(request):
    '''External node classifier for puppet. Takes a required request parameter
    'name', finds all node_groups associated witht he node, and all tags merged
    based on the following hierarchy:

        node_group
        data_center
        node

    Optional request parameter 'param_sources' will add an additional key that
    identifies what level of the hierarchy each tag comes from. Returns a
    dict.'''

    settings = request.registry.settings
    try:
        try:
            name = request.params['name']
        except KeyError as ex:
            msg = "Bad Request. Parameter 'name' is required."
            LOG.error(msg)
            return api_400(msg=msg)

        try:
            param_sources = request.params['param_sources']
        except KeyError:
            param_sources = False

        LOG.debug('Starting enc for node: {0}'.format(name))
        try:
            results = process_node_enc(settings, name, param_sources=param_sources)
        except (AttributeError, KeyError) as ex:
            return api_501(msg=repr(ex))
    except Exception as ex:
        msg = 'Error calling enc! Exception: {0}'.format(repr(ex))
        LOG.error(msg)
        return api_500(msg=msg)

    return api_200(results=results)
