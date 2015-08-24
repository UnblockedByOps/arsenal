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
    api_read_by_id,
    api_read_by_params,
    api_delete_by_id,
    api_delete_by_params,
    )
from arsenalweb.models import (
    DBSession,
    Tag,
    )


@view_config(route_name='api_tags', request_method='GET', request_param='schema=true', renderer='json')
def api_tag_schema(request):
    """Schema document for tags API"""

    tag = {
    }

    return tag


@view_config(route_name='api_tag_r', request_method='GET', renderer='json')
def api_tag_read_attrib(request):
    """Process read requests for the /api/tags/{id}/{resource} route."""

    return get_api_attribute(request, 'Tag')


@view_config(route_name='api_tag', request_method='GET', renderer='json')
def api_tag_read_id(request):
    """Process read requests for the /api/tags/{id} route."""

    return api_read_by_id(request, 'Tag')


@view_config(route_name='api_tags', request_method='GET', renderer='json')
def api_tag_read(request):
    """Process read requests for the /api/tags route."""

    return api_read_by_params(request, 'Tag')


@view_config(route_name='api_tags', permission='api_write', request_method='PUT', renderer='json')
def api_node_tags_write(request):
    """Process write requests for the /api/tags route."""

    au = get_authenticated_user(request)

    try:
        payload = request.json_body
        tag_name = payload['tag_name']
        tag_value = payload['tag_value']

        log.info('Searching for tag tag_name={0}'.format(tag_name))

        try:
            t = DBSession.query(Tag)
            t = t.filter(Tag.tag_name==tag_name)
            t = t.filter(Tag.tag_value==tag_value)
            t = t.one()
        except NoResultFound:
            try:
                log.info('Creating new tag tag_name={0},tag_value={1}'.format(tag_name, tag_value))
                utcnow = datetime.utcnow()

                t = Tag(tag_name=tag_name,
                        tag_value=tag_value,
                        updated_by=au['user_id'],
                        created=utcnow,
                        updated=utcnow)

                DBSession.add(t)
                DBSession.flush()
            except Exception as e:
                log.error('Error creating new tag tag_name={0},tag_value={1},exception={2}'.format(tag_name, tag_value, e))
                raise
        # Since there are no fields to update other than the two that
        # constitue a unqiue tag we return a 409 when an update would
        # have otherwise happened and handle it in client/UI.
        else:
            return Response(content_type='application/json', status_int=409)

        return t

    except Exception as e:
        log.error('Error writing to tags API={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_tag', permission='api_write', request_method='DELETE', renderer='json')
def api_tags_delete_id(request):
    """Process delete requests for the /api/tags/{id} route."""

    return api_delete_by_id(request, 'Tag')


@view_config(route_name='api_tags', permission='api_write', request_method='DELETE', renderer='json')
def api_tags_delete(request):
    """Process delete requests for the /api/tags route. Iterates
       over passed parameters."""

    return api_delete_by_params(request, 'Tag')


