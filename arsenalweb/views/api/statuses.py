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
    Status,
    )

@view_config(route_name='api_statuses', request_method='GET', renderer='json')
@view_config(route_name='api_statuses', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='api_status', request_method='GET', renderer='json')
@view_config(route_name='api_status', request_method='GET', request_param='format=json', renderer='json')
def api_status_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone("start"))
    except:
        pass

    try:
        if request.path == '/api/statuses':

            status_name = request.params.get('status_name')

            if status_name:
                log.info('Querying for status: {0}'.format(request.url))
                try:
                    q = DBSession.query(Status)
                    q = q.filter(Status.status_name==status_name)
                    return q.one()
                except Exception, e:
                    log.error('Error querying status={0},exception={2}'.format(request.url, e))
                    raise
            else:
                log.info('Displaying all statuses')
                try:
                    q = DBSession.query(Status)
                    statuses = q.limit(perpage).offset(offset).all()
                    return statuses
                except Exception, e:
                    log.error('Error querying status={0},exception={2}'.format(request.url, e))
                    raise

        if request.matchdict['id']:

            log.info('Displaying single status')
            try:
                q = DBSession.query(Status).filter(Status.status_id==request.matchdict['id'])
                status = q.one()
                return status
            except Exception, e:
                log.error('Error querying status={0},exception={2}'.format(request.url, e))
                raise

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)
    except Exception, e:
        conn_err_msg = e
        return Response(str(conn_err_msg), content_type='text/plain', status_int=500)


@view_config(route_name='api_statuses', permission='api_write', request_method='PUT', renderer='json')
def api_status_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body
        status_name = payload['status_name']
        description = payload['description']

        if request.path == '/api/statuses':

            log.info('Checking for status_name={0},description={1}'.format(status_name, description))
            try:
                s = DBSession.query(Status.status_name==status_name)
                s.one()
            except NoResultFound, e:
                try:
                    log.info("Creating new status: {0}".format(status_name))
                    utcnow = datetime.utcnow()
                    s = Status(status_name=status_name,
                               description=description,
                               updated_by=au['user_id'],
                               created=utcnow,
                               updated=utcnow)
                    DBSession.add(s)
                    DBSession.flush()
                except Exception, e:
                    log.error('Error creating status_name={0},description={1},exception={2}'.format(status_name, description, e))
                    raise
            # Update
            else:
                try:
                    log.info('Updating status_name={0},description={1}'.format(status_name, description))

                    s.status_name = payload['status_name']
                    s.description = payload['description']
                    s.updated_by=au['user_id']

                    DBSession.flush()

                except Exception, e:
                    log.error('Error updating status_name={0},description={1},exception={2}'.format(status_name, description, e))
                    raise

            return s

    except Exception, e:
        return Response(str(e), content_type='text/plain', status_int=500)


@view_config(route_name='api_statuses', permission='api_write', request_method='DELETE', renderer='json')
def api_status_delete(request):

    # Will be used for auditing
    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/statuses':

            try:
                status_name = payload['status_name']

                log.info('Checking for status_name={0}'.format(status_name))
                s = DBSession.query(Status.status_name==status_name)
                s.one()
            except NoResultFound, e:
                return Response(content_type='application/json', status_int=404)

            else:
                try:
                    # FIXME: Need auditing
                    # FIXME: What about orphaned assigments?
                    log.info('Deleting status_name={0}'.format(status_name))
                    DBSession.delete(s)
                    DBSession.flush()
                except Exception, e:
                    log.info('Error deleting status_name={0}'.format(status_name))
                    raise

            # FIXME: Return none is 200 or ?
            # return nga

    except Exception, e:
        log.error('Error with node_group_assignment API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)
