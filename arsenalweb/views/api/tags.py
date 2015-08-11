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
    Tag,
    )

@view_config(route_name='api_tags', request_method='GET', renderer='json')
@view_config(route_name='api_tag', request_method='GET', renderer='json')
def api_tag_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        if request.path == '/api/tags':

            exact_get =  request.GET.get("exact_get", None)
            tag_name = request.params.get('tag_name')
            tag_value = request.params.get('tag_value')

            if any((tag_name, tag_value)):
                log.info('Querying for tag_name: {0}'.format(request.url))
                s = ""
                try:
                    t = DBSession.query(Tag)
                    for k,v in request.GET.items():
                        # FIXME: This is sub-par. Need a better way to distinguish
                        # meta params from search params without having to
                        # pre-define everything.
                        if k == 'exact_get':
                            continue
    
                        s+='{0}={1},'.format(k, v)
                        if exact_get:
                            log.info('Exact filtering on {0}={1}'.format(k, v))
                            t = t.filter(getattr(Tag ,k)==v)
                        else:
                            log.info('Loose filtering on {0}={1}'.format(k, v))
                            t = t.filter(getattr(Tag ,k).like('%{0}%'.format(v)))
                    log.info('Searching for tags with params: {0}'.format(s.rstrip(',')))
                    return t.all()
                except Exception as e:
                    log.error('Error querying tag_name={0},exception={1}'.format(request.url, e))
                    raise
            else:
                log.info('Displaying all tags')
                try:
                    ts = DBSession.query(Tag)
                    ts = ts.limit(perpage).offset(offset).all()
                    return ts
                except Exception as e:
                    log.error('Error querying tags={0},exception={1}'.format(request.url, e))
                    raise

        if request.matchdict['id']:

            tag_id = request.matchdict['id']
            log.info('Displaying single tag tag_id={0}'.format(tag_id))

            try:
                t = DBSession.query(Tag)
                t = t.filter(Tag.tag_id==tag_id)
                t = t.one()
                return t
            except Exception as e:
                log.error('Error querying tag={0},exception={1}'.format(request.url, e))
                raise

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error querying tags api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tags', permission='api_write', request_method='PUT', renderer='json')
def api_node_tags_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/tags':

            try:
                tag_name = payload['tag_name']
                tag_value = payload['tag_value']

                log.info('Checking for tag_name: {0}'.format(tag_name))
                t = DBSession.query(Tag)
                t = t.filter(Tag.tag_name==tag_name)
                t = t.filter(Tag.tag_value==tag_value)
                t = t.one()
            except NoResultFound:
                try:
                    log.info('Creating new tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                    utcnow = datetime.utcnow()
                    t = Tag(tag_name=tag_name,
                            tag_value=tag_value,
                            updated_by=au['user_id'],
                            created=utcnow,
                            updated=utcnow)
                    DBSession.add(t)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error creating new tag tag_name={0},tag_value={1},exception={3}'.format(tag_name, tag_value, e))
                    raise
            # FIXME: By definition this will never get hit becasue there are 
            # no fields to update other than the two that constitue a unqiue
            # tag. Perhaps just return a 200?
            else:
                try:
                    log.info('Updating tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                    t.tag_name = tag_name
                    t.tag_value = tag_value
                    t.updated_by=au['user_id']
                    DBSession.flush()
                except Exception as e:
                    log.error('Error updating tag tag_name={0},tag_value={1},exception={2}'.format(tag_name, tag_value, e))
                    raise

            return t

    except Exception as e:
        log.error('Error with tag API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tags', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_tag', permission='api_write', request_method='DELETE', renderer='json')
def api_tags_delete(request):

    # Will be used for auditing
    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/tags':

            try:
                tag_name = payload['tag_name']
                tag_value = payload['tag_value']

                log.info('Checking for tag tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                t = DBSession.query(Tag)
                t = t.filter(Tag.tag_name==tag_name)
                t = t.filter(Tag.tag_value==tag_value)
                t = t.one()
            except NoResultFound:
                return Response(content_type='application/json', status_int=404)

            else:
                try:
                    # FIXME: Need auditing
                    # FIXME: What about orphaned assigments?
                    log.info('Deleting tag tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                    DBSession.delete(t)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error deleting tag tag_name={0},tag_value={1},exception={2}'.format(tag_name, tag_value, e))
                    raise

        if request.matchdict['id']:

           try:
               tag_id = request.matchdict['id']

               log.info('Checking for tag_id={0}'.format(tag_id))
               t = DBSession.query(Tag)
               t = t.filter(Tag.tag_id==tag_id)
               t = t.one()
           except NoResultFound:
               return Response(content_type='application/json', status_int=404)

           else:
               try:
                   # FIXME: Need auditing
                   # FIXME: What about orphaned assigments?
                   log.info('Deleting tag tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                   DBSession.delete(t)
                   DBSession.flush()
               except Exception as e:
                   log.error('Error deleting tag tag_name={0},tag_value={1},exception={2}'.format(tag_name, tag_value, e))
                   raise

            # FIXME: Return none is 200 or ?
            # return t

    except Exception as e:
        log.error('Error with tag API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)
