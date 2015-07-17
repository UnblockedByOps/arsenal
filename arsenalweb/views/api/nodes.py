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
import json
from datetime import datetime
from arsenalweb.views import (
    get_authenticated_user,
    log,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    )

@view_config(route_name='api_nodes', request_method='GET', renderer='json')
@view_config(route_name='api_nodes', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_nodes', request_method='GET', request_param='format=xml', renderer='xml')
@view_config(route_name='api_node', request_method='GET', renderer='json')
@view_config(route_name='api_node', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_node', request_method='GET', request_param='format=xml', renderer='xml')
def api_node_read(request):

    au = get_authenticated_user(request)

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone("start"))
    except:
        pass

    try:
        if request.path == '/api/nodes':
            log.info('Displaying all nodes')
            try:
                q = DBSession.query(Node)
                nodes = q.limit(perpage).offset(offset).all()
                return nodes
            except Exception, e:
                conn_err_msg = e
                return Response(str(conn_err_msg), content_type='text/plain', status_int=500)

        if request.matchdict['id']:
            log.info('Displaying single node')
            try:
                q = DBSession.query(Node).filter(Node.node_id==request.matchdict['id'])
                node = q.one()
                return node
            except Exception, e:
                conn_err_msg = e
                return Response(str(conn_err_msg), content_type='text/plain', status_int=500)
            
    except Exception, e:
        conn_err_msg = e
        return Response(str(conn_err_msg), content_type='text/plain', status_int=500)

    return {'read_api':'true'}


@view_config(route_name='api_nodes', permission='api_write', request_method='PUT', renderer='json')
def api_node_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/nodes':

            q = DBSession.query(Node).filter(Node.unique_id==payload['unique_id'])
            check = DBSession.query(q.exists()).scalar()
            # Create
            if not check:
                log.info("Creating new node: {0}".format(payload['unique_id']))
                utcnow = datetime.utcnow()
                n = Node(unique_id=payload['unique_id'],
                         name=payload['name'],
                         uptime=payload['uptime'],
                         updated_by=au['user_id'],
                         created=utcnow,
                         updated=utcnow)
                DBSession.add(n)
                DBSession.flush()
            # Update
            else:
                log.info("Updating node: {0}".format(payload['unique_id']))
                n = DBSession.query(Node).filter(Node.unique_id==payload['unique_id']).one()
                n.name = payload['name']
                n.uptime = payload['uptime']
                n.updated_by=au['user_id']
                DBSession.flush()

            return json.dumps(n, default=lambda o: o.__dict__)
    except:

        return {'':''}

