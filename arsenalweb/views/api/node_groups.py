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


@view_config(route_name='api_node_groups', request_method='GET', request_param='schema=true', renderer='json')
def api_node_group_schema(request):

    node_group = {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "id": "https://REPLACE",
      "type": "object",
      "properties": {
        "updated": {
          "id": "https://REPLACE/updated",
          "type": "string",
          "default": "2015-07-30 15:00:37 -07:00"
        },
        "node_group_owner": {
          "id": "https://REPLACE/node_group_owner",
          "type": "string",
          "default": "aaron.bandt@citygridmedia.com"
        },
        "description": {
          "id": "https://REPLACE/description",
          "type": "string",
          "default": "Default Install"
        },
        "tags": {
          "id": "https://REPLACE/tags",
          "type": "array",
          "items": [
            {
              "id": "https://REPLACE/tags/0",
              "type": "object",
              "properties": {
                "updated": {
                  "id": "https://REPLACE/tags/0/updated",
                  "type": "string",
                  "default": "2015-08-11 13:44:35 -07:00"
                },
                "updated_by": {
                  "id": "https://REPLACE/tags/0/updated_by",
                  "type": "string",
                  "default": "Admin"
                },
                "created": {
                  "id": "https://REPLACE/tags/0/created",
                  "type": "string",
                  "default": "2015-08-11 13:44:35 -07:00"
                },
                "tag_name": {
                  "id": "https://REPLACE/tags/0/tag_name",
                  "type": "string",
                  "default": "ct_BusinessUnit"
                },
                "tag_id": {
                  "id": "https://REPLACE/tags/0/tag_id",
                  "type": "integer",
                  "default": 1
                },
                "tag_value": {
                  "id": "https://REPLACE/tags/0/tag_value",
                  "type": "string",
                  "default": "CityGrid"
                }
              }
            },
            {
              "id": "https://REPLACE/tags/1",
              "type": "object",
              "properties": {
                "updated": {
                  "id": "https://REPLACE/tags/1/updated",
                  "type": "string",
                  "default": "2015-08-11 13:44:35 -07:00"
                },
                "updated_by": {
                  "id": "https://REPLACE/tags/1/updated_by",
                  "type": "string",
                  "default": "Admin"
                },
                "created": {
                  "id": "https://REPLACE/tags/1/created",
                  "type": "string",
                  "default": "2015-08-11 13:44:35 -07:00"
                },
                "tag_name": {
                  "id": "https://REPLACE/tags/1/tag_name",
                  "type": "string",
                  "default": "ct_BusinessUnit"
                },
                "tag_id": {
                  "id": "https://REPLACE/tags/1/tag_id",
                  "type": "integer",
                  "default": 2
                },
                "tag_value": {
                  "id": "https://REPLACE/tags/1/tag_value",
                  "type": "string",
                  "default": "Citysearch"
                }
              }
            }
          ]
        },
        "created": {
          "id": "https://REPLACE/created",
          "type": "string",
          "default": "2015-07-30 15:00:37 -07:00"
        },
        "updated_by": {
          "id": "https://REPLACE/updated_by",
          "type": "string",
          "default": "kaboom"
        },
        "node_group_id": {
          "id": "https://REPLACE/node_group_id",
          "type": "integer",
          "default": 2
        },
        "node_group_name": {
          "id": "https://REPLACE/node_group_name",
          "type": "string",
          "default": "default_install"
        }
      },
      "required": [
        "updated",
        "node_group_owner",
        "description",
        "tags",
        "created",
        "updated_by",
        "node_group_id",
        "node_group_name"
      ]
    }

    return node_group


@view_config(route_name='api_node_group_r', request_method='GET', renderer='json')
def api_node_group_read_attrib(request):
    print "YUPPERZ"

    node_group_id = request.matchdict['id']
    resource = request.matchdict['resource']
    log.info('Querying for node_group attribute={0},url={1}'.format(resource, request.url))

    try:
        ng = DBSession.query(NodeGroup)
        ng = ng.filter(NodeGroup.node_group_id==node_group_id)
        ng = ng.one()
        return { resource: getattr(ng, resource) }
    except (NoResultFound, AttributeError):
        return Response(content_type='application/json', status_int=404)
    except Exception as e:
        log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
        raise


@view_config(route_name='api_node_groups', request_method='GET', renderer='json')
@view_config(route_name='api_node_group', request_method='GET', renderer='json')
def api_node_group_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone('start'))
    except:
        pass

    try:
        if request.path == '/api/node_groups':

            node_group_name = request.params.get('node_group_name')
            
            if node_group_name:
                log.info('Querying for node_group: {0}'.format(request.url))
                try:
                    ng = DBSession.query(NodeGroup)
                    ng = ng.filter(NodeGroup.node_group_name==node_group_name)
                    return ng.all()
                except Exception as e:
                    log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
                    raise
            else:
                log.info('Displaying all node_groups')
                try:
                    ngs = DBSession.query(NodeGroup)
                    ngs = ngs.limit(perpage).offset(offset).all()
                    return ngs
                except Exception as e:
                    log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
                    raise

        if request.matchdict['id']:

            node_group_id = request.matchdict['id']
            log.info('Displaying single node_group node_group_id={0}'.format(node_group_id))

            try:
                ng = DBSession.query(NodeGroup)
                ng = ng.filter(NodeGroup.node_group_id==node_group_id)
                ng = ng.one()
                return ng
            except Exception as e:
                log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
                raise

    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception as e:
        log.error('Error querying node_groups api={0},exception={1}'.format(request.url, e))
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
                node_group_description = payload['node_group_description']

                log.info('Checking for node_group_name: {0}'.format(node_group_name))
                q = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name)
                q.one()
            except NoResultFound:
                try:
                    log.info('Creating new node_group: {0}'.format(node_group_name))
                    utcnow = datetime.utcnow()
                    ng = NodeGroup(node_group_name=node_group_name,
                                   node_group_owner=node_group_owner,
                                   description=node_group_description,
                                   updated_by=au['user_id'],
                                   created=utcnow,
                                   updated=utcnow)
                    DBSession.add(ng)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error creating new node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, node_group_description, e))
                    raise
            else:
                try:
                    log.info('Updating node_group: {0}'.format(node_group_name))
                    ng = DBSession.query(NodeGroup).filter(NodeGroup.node_group_name==node_group_name).one()
                    ng.node_group_name = node_group_name
                    ng.node_group_owner = node_group_owner
                    ng.description = node_group_description
                    ng.updated_by=au['user_id']
                    DBSession.flush()
                except Exception as e:
                    log.error('Error updating node_group node_group_name={0},node_group_owner={1},description={2},exception={3}'.format(node_group_name, node_group_owner, node_group_description, e))
                    raise

            return ng

    except Exception as e:
        log.error('Error with node_group API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_node_groups', permission='api_write', request_method='DELETE', renderer='json')
@view_config(route_name='api_node_group', permission='api_write', request_method='DELETE', renderer='json')
def api_node_groups_delete(request):

    # Will be used for auditing
    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/node_groups':

            try:
                node_group_name = payload['node_group_name']

                log.info('Checking for node_group_name: {0}'.format(node_group_name))
                ng = DBSession.query(NodeGroup)
                ng = ng.filter(NodeGroup.node_group_name==node_group_name)
                ng = ng.one()
            except NoResultFound:
                return Response(content_type='application/json', status_int=404)

            else:
                try:
                    # FIXME: Need auditing
                    # FIXME: What about orphaned assigments?
                    log.info('Deleting node_group: {0}'.format(node_group_name))
                    DBSession.delete(ng)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error deleting node_group node_group_name={0},exception={1}'.format(node_group_name, e))
                    raise

        if request.matchdict['id']:

           try:
               node_group_id = request.matchdict['id']

               log.info('Checking for node_group_id={0}'.format(node_group_id))
               ng = DBSession.query(NodeGroup)
               ng = ng.filter(NodeGroup.node_group_id==node_group_id)
               ng = ng.one()
           except NoResultFound:
               return Response(content_type='application/json', status_int=404)

           else:
               try:
                   # FIXME: Need auditing
                   # FIXME: What about orphaned assigments?
                   log.info('Deleting node_group_name={0}'.format(ng.node_group_name))
                   DBSession.delete(ng)
                   DBSession.flush()
               except Exception as e:
                   log.error('Error deleting node_group node_group_name={0},exception={1}'.format(ng.node_group_name, e))
                   raise

            # FIXME: Return none is 200 or ?
            # return ng

    except Exception as e:
        log.error('Error with node_group API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)
