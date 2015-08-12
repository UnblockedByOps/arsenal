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
from arsenalweb.views.api import (
    get_api_attribute,
    )
from arsenalweb.models import (
    DBSession,
    NodeGroupAssignment,
    )


@view_config(route_name='api_node_group_assignment_r', request_method='GET', renderer='json')
def api_node_group_assignment_read_attrib(request):

     return get_api_attribute(request, 'NodeGroupAssignment')


@view_config(route_name='api_node_group_assignment', request_method='GET', renderer='json')
def api_node_group_assignment_read_id(request):

    try:
        log.info('Displaying single node group assignment')
        nga = DBSession.query(NodeGroupAssignment)
        nga = nga.filter(NodeGroupAssignment.node_group_assignment_id==request.matchdict['id'])
        nga = nga.one()

        return nga

    except NoResultFound:
            return Response(content_type='application/json', status_int=404)

    except Exception, e:
        log.error('Error querying api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_group_assignments', request_method='GET', renderer='json')
def api_node_group_assignment_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        # FIXME: need to be able to search for individual assignments
        node_id = request.params.get('node_id')
        node_group_id = request.params.get('node_group_id')
        exact_get =  request.GET.get("exact_get", None)

        s = ''
        nga = DBSession.query(NodeGroupAssignment)
        if any((node_id, node_group_id)):

            # FIXME: this is starting to get replicated. Can it be a function?
            for k,v in request.GET.items():
                # FIXME: This is sub-par. Need a better way to distinguish
                # meta params from search params without having to
                # pre-define everything.
                if k == 'exact_get':
                    continue

                s+='{0}={1},'.format(k, v)
                if exact_get:
                    log.info('Exact filtering on {0}={1}'.format(k, v))
                    nga = nga.filter(getattr(NodeGroupAssignment ,k)==v)
                else:
                    log.info('Loose filtering on {0}={1}'.format(k, v))
                    nga = nga.filter(getattr(NodeGroupAssignment ,k).like('%{0}%'.format(v)))

            log.info('Searching for node_group_assignments with params: {0}'.format(s.rstrip(',')))

        else:
            log.info('Displaying all node_group_assignments')

        nga = nga.limit(perpage).offset(offset).all()

        return nga

    except NoResultFound:
            return Response(content_type='application/json', status_int=404)

    except Exception, e:
        log.error('Error querying api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_group_assignments', permission='api_write', request_method='PUT', renderer='json')
def api_node_group_assignments_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/node_group_assignments':

            try:
                node_id = payload['node_id']
                node_group_id = payload['node_group_id']

                log.info('Checking for node_group_assignment node_id={0},node_group_id={1}'.format(node_id, node_group_id))
                q = DBSession.query(NodeGroupAssignment)
                q = q.filter(NodeGroupAssignment.node_id==node_id)
                q = q.filter(NodeGroupAssignment.node_group_id==node_group_id)
                q.one()
                log.info('node_group_assignment already exists')
            except NoResultFound, e:
                try:
                    log.info('Creating new node_group_assignment for node_id: {0} node_group_id {1}'.format(node_id, node_group_id))
                    utcnow = datetime.utcnow()
                    nga = NodeGroupAssignment(node_id=node_id,
                                              node_group_id=node_group_id,
                                              updated_by=au['user_id'],
                                              created=utcnow,
                                              updated=utcnow)
                    DBSession.add(nga)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error creating new node_group_assignment node_id={0},node_group_id={1},exception={2}'.format(node_id, node_group_id, e))
                    raise

    except Exception, e:
        log.error('Error with node_group_assignment API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_group_assignments', permission='api_write', request_method='DELETE', renderer='json')
def api_node_group_assignments_delete(request):

    # Will be used for auditing
    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/node_group_assignments':

            try:
                node_id = payload['node_id']
                node_group_id = payload['node_group_id']

                log.info('Checking for node_group_assignment node_id={0},node_group_id={1}'.format(node_id, node_group_id))
                nga = DBSession.query(NodeGroupAssignment)
                nga = nga.filter(NodeGroupAssignment.node_id==node_id)
                nga = nga.filter(NodeGroupAssignment.node_group_id==node_group_id)
                nga = nga.one()
            except NoResultFound, e:
                return Response(content_type='application/json', status_int=404)

            else:
                try:
                    # FIXME: Need auditing
                    log.info('Deleting node_group_assignment node_id={0},node_group_id={1}'.format(node_id, node_group_id))
                    DBSession.delete(nga)
                    DBSession.flush()
                except Exception, e:
                    log.info('Error deleting node_group_assignment node_id={0},node_group_id={1}'.format(node_id, node_group_id))
                    raise

            # FIXME: Return none is 200?
            # return nga

    except Exception, e:
        log.error('Error with node_group_assignment API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)
