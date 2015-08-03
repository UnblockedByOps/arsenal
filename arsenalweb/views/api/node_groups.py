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
    )
from arsenalweb.models import (
    DBSession,
    NodeGroup,
    )

@view_config(route_name='api_node_groups', request_method='GET', renderer='json')
@view_config(route_name='api_node_groups', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_node_group', request_method='GET', renderer='json')
@view_config(route_name='api_node_group', request_method='GET', request_param='format=json', renderer='json')
def api_node_group_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        if request.path == '/api/node_groups':
            log.info('Displaying all node_groups')
            try:
                q = DBSession.query(NodeGroup)
                node_groups = q.limit(perpage).offset(offset).all()
                return node_groups
            except NoResultFound:
                return Response(content_type='application/json', status_int=404)

        if request.matchdict['id']:
            log.info('Displaying single node group')
            try:
                q = DBSession.query(NodeGroup).filter(NodeGroup.node_group_id==request.matchdict['id'])
                node_group = q.one()
                return node_group
            except NoResultFound:
                return Response(content_type='application/json', status_int=404)
            
    except Exception, e:
        log.error('Error querying api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_groups', permission='api_write', request_method='PUT', renderer='json')
def api_node_groups_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/node_groups':

            try:
                node_group_name = payload['node_group_name']
                node_group_owner = payload['node_group_owner']
                description = payload['description']

                log.info('Checking for node_group_name: {0}'.format(node_group_name))
                q = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name)
                q.one()
            except NoResultFound, e:
                try:
                    log.info('Creating new node_group: {0}'.format(node_group_name))
                    utcnow = datetime.utcnow()
                    ng = NodeGroup(node_group_name=node_group_name,
                                   node_group_owner=node_group_owner,
                                   description=description,
                                   updated_by=au['user_id'],
                                   created=utcnow,
                                   updated=utcnow)
                    DBSession.add(ng)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error creating new node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, description, e))
                    raise
            else:
                try:
                    log.info('Updating node_group: {0}'.format(node_group_name))
                    ng = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name).one()
                    ng.node_group_name = node_group_name
                    ng.node_group_owner = node_group_owner
                    ng.description = description
                    ng.updated_by=au['user_id']
                    DBSession.flush()
                except Exception, e:
                    log.error('Error updating node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, description, e))
                    raise

            return ng

    except Exception, e:
        log.error('Error with node_group API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_groups', permission='api_write', request_method='DELETE', renderer='json')
def api_node_groups_delete(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/node_groups':

            try:
                node_group_name = payload['node_group_name']

                log.info('Checking for node_group_name: {0}'.format(node_group_name))
                q = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name)
                q.one()
            except NoResultFound, e:
                return Response(content_type='application/json', status_int=404)

            else:
                try:
                    # FIXME: Need auditing
                    log.info('Deleting node_group: {0}'.format(node_group_name))
                    ng = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name).one()
                    DBSession.delete(ng)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error deleting node_group node_group_name={0}exception={1}'.format(node_group_name, e))
                    raise

            return ng

    except Exception, e:
        log.error('Error with node_group API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)
