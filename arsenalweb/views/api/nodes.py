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
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    get_authenticated_user,
    log,
    _api_get,
    _api_put,
    )
from arsenalweb.views.api import (
    get_api_attribute,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    Status,
    )

@view_config(route_name='api_nodes', request_method='GET', request_param='schema=true', renderer='json')
def api_node_schema(request):
    """Document the API poc."""

    log.info('schema requested')

    node = {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "id": "https://REPLACE",
      "type": "object",
      "properties": {
        "status": {
          "id": "https://REPLACE/status",
          "type": "object",
          "properties": {
            "updated": {
              "id": "https://REPLACE/status/updated",
              "type": "string"
            },
            "description": {
              "id": "https://REPLACE/status/description",
              "type": "string"
            },
            "status_id": {
              "id": "https://REPLACE/status/status_id",
              "type": "integer"
            },
            "status_name": {
              "id": "https://REPLACE/status/status_name",
              "type": "string"
            },
            "updated_by": {
              "id": "https://REPLACE/status/updated_by",
              "type": "string"
            },
            "created": {
              "id": "https://REPLACE/status/created",
              "type": "string"
            }
          },
          "required": [
            "updated",
            "description",
            "status_id",
            "status_name",
            "updated_by",
            "created"
          ]
        },
        "uptime": {
          "id": "https://REPLACE/uptime",
          "type": "string"
        },
        "operating_system": {
          "id": "https://REPLACE/operating_system",
          "type": "object",
          "properties": {
            "version_number": {
              "id": "https://REPLACE/operating_system/version_number",
              "type": "string"
            },
            "description": {
              "id": "https://REPLACE/operating_system/description",
              "type": "string"
            },
            "operating_system_id": {
              "id": "https://REPLACE/operating_system/operating_system_id",
              "type": "integer"
            },
            "created": {
              "id": "https://REPLACE/operating_system/created",
              "type": "string"
            },
            "variant": {
              "id": "https://REPLACE/operating_system/variant",
              "type": "string"
            },
            "updated": {
              "id": "https://REPLACE/operating_system/updated",
              "type": "string"
            },
            "architecture": {
              "id": "https://REPLACE/operating_system/architecture",
              "type": "string"
            },
            "updated_by": {
              "id": "https://REPLACE/operating_system/updated_by",
              "type": "string"
            }
          }
        },
        "updated_by": {
          "id": "https://REPLACE/updated_by",
          "type": "string"
        },
        "operating_system_id": {
          "id": "https://REPLACE/operating_system_id",
          "type": "integer"
        },
        "tags": {
          "id": "https://REPLACE/tags",
          "type": "array",
          "items": {
            "id": "https://REPLACE/tags/0",
            "type": "object",
            "properties": {
              "updated": {
                "id": "https://REPLACE/tags/0/updated",
                "type": "string"
              },
              "updated_by": {
                "id": "https://REPLACE/tags/0/updated_by",
                "type": "string"
              },
              "created": {
                "id": "https://REPLACE/tags/0/created",
                "type": "string"
              },
              "tag_name": {
                "id": "https://REPLACE/tags/0/tag_name",
                "type": "string"
              },
              "tag_id": {
                "id": "https://REPLACE/tags/0/tag_id",
                "type": "integer"
              },
              "tag_value": {
                "id": "https://REPLACE/tags/0/tag_value",
                "type": "string"
              }
            }
          }
        },
        "hardware_profile": {
          "id": "https://REPLACE/hardware_profile",
          "type": "object",
          "properties": {
            "updated": {
              "id": "https://REPLACE/hardware_profile/updated",
              "type": "string"
            },
            "updated_by": {
              "id": "https://REPLACE/hardware_profile/updated_by",
              "type": "string"
            },
            "created": {
              "id": "https://REPLACE/hardware_profile/created",
              "type": "string"
            },
            "hardware_profile_id": {
              "id": "https://REPLACE/hardware_profile/hardware_profile_id",
              "type": "integer"
            },
            "model": {
              "id": "https://REPLACE/hardware_profile/model",
              "type": "string"
            },
            "manufacturer": {
              "id": "https://REPLACE/hardware_profile/manufacturer",
              "type": "string"
            }
          }
        },
        "created": {
          "id": "https://REPLACE/created",
          "type": "string"
        },
        "updated": {
          "id": "https://REPLACE/updated",
          "type": "string"
        },
        "node_name": {
          "id": "https://REPLACE/node_name",
          "type": "string"
        },
        "node_id": {
          "id": "https://REPLACE/node_id",
          "type": "integer"
        },
        "status_id": {
          "id": "https://REPLACE/status_id",
          "type": "integer"
        },
        "node_groups": {
          "id": "https://REPLACE/node_groups",
          "type": "array",
          "items": [
            {
              "id": "https://REPLACE/node_groups/0",
              "type": "object",
              "properties": {
                "updated": {
                  "id": "https://REPLACE/node_groups/0/updated",
                  "type": "string"
                },
                "node_group_owner": {
                  "id": "https://REPLACE/node_groups/0/node_group_owner",
                  "type": "string"
                },
                "description": {
                  "id": "https://REPLACE/node_groups/0/description",
                  "type": "string"
                },
                "tags": {
                  "id": "https://REPLACE/node_groups/0/tags",
                  "type": "array",
                  "items": [
                    {
                      "id": "https://REPLACE/node_groups/0/tags/0",
                      "type": "object",
                      "properties": {
                        "updated": {
                          "id": "https://REPLACE/node_groups/0/tags/0/updated",
                          "type": "string"
                        },
                        "updated_by": {
                          "id": "https://REPLACE/node_groups/0/tags/0/updated_by",
                          "type": "string"
                        },
                        "created": {
                          "id": "https://REPLACE/node_groups/0/tags/0/created",
                          "type": "string"
                        },
                        "tag_name": {
                          "id": "https://REPLACE/node_groups/0/tags/0/tag_name",
                          "type": "string"
                        },
                        "tag_id": {
                          "id": "https://REPLACE/node_groups/0/tags/0/tag_id",
                          "type": "integer"
                        },
                        "tag_value": {
                          "id": "https://REPLACE/node_groups/0/tags/0/tag_value",
                          "type": "string"
                        }
                      }
                    },
                    {
                      "id": "https://REPLACE/node_groups/0/tags/1",
                      "type": "object",
                      "properties": {
                        "updated": {
                          "id": "https://REPLACE/node_groups/0/tags/1/updated",
                          "type": "string"
                        },
                        "updated_by": {
                          "id": "https://REPLACE/node_groups/0/tags/1/updated_by",
                          "type": "string"
                        },
                        "created": {
                          "id": "https://REPLACE/node_groups/0/tags/1/created",
                          "type": "string"
                        },
                        "tag_name": {
                          "id": "https://REPLACE/node_groups/0/tags/1/tag_name",
                          "type": "string"
                        },
                        "tag_id": {
                          "id": "https://REPLACE/node_groups/0/tags/1/tag_id",
                          "type": "integer"
                        },
                        "tag_value": {
                          "id": "https://REPLACE/node_groups/0/tags/1/tag_value",
                          "type": "string"
                        }
                      }
                    }
                  ]
                },
                "created": {
                  "id": "https://REPLACE/node_groups/0/created",
                  "type": "string"
                },
                "updated_by": {
                  "id": "https://REPLACE/node_groups/0/updated_by",
                  "type": "string"
                },
                "node_group_id": {
                  "id": "https://REPLACE/node_groups/0/node_group_id",
                  "type": "integer"
                },
                "node_group_name": {
                  "id": "https://REPLACE/node_groups/0/node_group_name",
                  "type": "string"
                }
              }
            },
            {
              "id": "https://REPLACE/node_groups/1",
              "type": "object",
              "properties": {
                "updated": {
                  "id": "https://REPLACE/node_groups/1/updated",
                  "type": "string"
                },
                "node_group_owner": {
                  "id": "https://REPLACE/node_groups/1/node_group_owner",
                  "type": "string"
                },
                "description": {
                  "id": "https://REPLACE/node_groups/1/description",
                  "type": "string"
                },
                "tags": {
                  "id": "https://REPLACE/node_groups/1/tags",
                  "type": "array",
                  "items": []
                },
                "created": {
                  "id": "https://REPLACE/node_groups/1/created",
                  "type": "string"
                },
                "updated_by": {
                  "id": "https://REPLACE/node_groups/1/updated_by",
                  "type": "string"
                },
                "node_group_id": {
                  "id": "https://REPLACE/node_groups/1/node_group_id",
                  "type": "integer"
                },
                "node_group_name": {
                  "id": "https://REPLACE/node_groups/1/node_group_name",
                  "type": "string"
                }
              }
            }
          ]
        },
        "hardware_profile_id": {
          "id": "https://REPLACE/hardware_profile_id",
          "type": "integer"
        },
        "unique_id": {
          "id": "https://REPLACE/unique_id",
          "type": "string"
        }
      },
      "required": [
        "node_name",
        "status_id",
        "unique_id"
      ]
    }

    return node


@view_config(route_name='api_node_r', request_method='GET', renderer='json')
def api_node_read_attrib(request):

     return get_api_attribute(request, 'Node')


@view_config(route_name='api_nodes', request_method='GET', renderer='json')
@view_config(route_name='api_node', request_method='GET', renderer='json')
def api_node_read(request):

    perpage = 40
    offset = 0

    try:
        offset = int(request.GET.getone("start"))
    except:
        pass

    try:
        if request.path == '/api/nodes':

            exact_get =  request.GET.get("exact_get", None)

            if request.params:
                s = ''
                # Filter on all the passed in terms
                q = DBSession.query(Node)

                for k,v in request.GET.items():
                    # FIXME: This is sub-par. Need a better way to distinguish 
                    # meta params from search params without having to
                    # pre-define everything.
                    if k == 'exact_get':
                        continue

                    s+='{0}={1},'.format(k, v)    
                    if exact_get:
                        log.info('Exact filtering on {0}={1}'.format(k, v))
                        q = q.filter(getattr(Node ,k)==v)
                    else:
                        log.info('Loose filtering on {0}={1}'.format(k, v))
                        q = q.filter(getattr(Node ,k).like('%{0}%'.format(v)))
                log.info('Searching for node with params: {0}'.format(s.rstrip(',')))
                nodes = q.all()
                return nodes
            else:
                log.info('Displaying all nodes')
                q = DBSession.query(Node)
                nodes = q.limit(perpage).offset(offset).all()
                return nodes

        if request.matchdict['id']:

            log.info('Displaying single node')
            q = DBSession.query(Node).filter(Node.node_id==request.matchdict['id'])
            node = q.one()
            return node
            
    except NoResultFound:
        return Response(content_type='application/json', status_int=404)

    except Exception, e:
        log.error('Error querying api={0},exception={1}'.format(request.url, e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_nodes', permission='api_write', request_method='PUT', renderer='json')
@view_config(route_name='api_node', permission='api_write', request_method='PUT', renderer='json')
def api_node_write(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        # FIXME: right now /api/nodes expects all paramters to be passed, no piecemeal updates.
        # Also no support for bulk updates
        if request.path == '/api/nodes':

            if payload['register']:

                # Get the hardware_profile_id or create if it doesn't exist.
                try:
                    manufacturer = payload['hardware_profile']['manufacturer']
                    model = payload['hardware_profile']['model']

                    uri = '/api/hardware_profiles'
                    data = {'manufacturer': manufacturer,
                            'model': model
                    }
                    hardware_profile = _api_get(request, uri, data)

                    if not hardware_profile:
                        log.info('hardware_profile not found, creating')
                        data_j = json.dumps(data, default=lambda o: o.__dict__)
                        _api_put(request, uri, data=data_j)
                        hardware_profile = _api_get(request, uri, data)

                    hardware_profile_id = hardware_profile['hardware_profile_id']
                    log.info('hardware_profile is: {0}'.format(hardware_profile))
                except Exception, e:
                    log.error('Unable to determine hardware_profile manufacturer={0},model={1},exception={2}'.format(manufacturer, model, e))
                    raise

                # Get the operating_system_id or create if it doesn't exist.
                try:
                    variant = payload['operating_system']['variant']
                    version_number = payload['operating_system']['version_number']
                    architecture = payload['operating_system']['architecture']
                    description = payload['operating_system']['description']

                    uri = '/api/operating_systems'
                    data = {'variant': variant,
                            'version_number': version_number,
                            'architecture': architecture,
                            'description': description
                    }
                    operating_system = _api_get(request, uri, data)

                    if not operating_system:
    
                        log.info('operating_system not found, attempting to create')
                        data_j = json.dumps(data, default=lambda o: o.__dict__)
                        _api_put(request, uri, data=data_j)
                        operating_system = _api_get(request, uri, data)

                    operating_system_id = operating_system['operating_system_id']
                    log.info('operating_system is: {0}'.format(operating_system))
                except Exception, e:
                    log.error('Unable to determine operating_system variant={0},version_number={1},architecture={2},description={3},exception={4}'.format(variant, version_number, architecture, description, e))
                    raise

                try:
                    unique_id = payload['unique_id']
                    node_name = payload['node_name']
                    uptime = payload['uptime']

                    log.info('Checking for unique_id: {0}'.format(unique_id))
                    q = DBSession.query(Node).filter(Node.unique_id==unique_id)
                    q.one()
                except NoResultFound, e:
                    try:
                        log.info('Creating new node: {0}'.format(unique_id))
                        utcnow = datetime.utcnow()
                        n = Node(unique_id=unique_id,
                                 node_name=node_name,
                                 hardware_profile_id=hardware_profile_id,
                                 operating_system_id=operating_system_id,
                                 uptime=uptime,
                                 status_id=2,
                                 updated_by=au['user_id'],
                                 created=utcnow,
                                 updated=utcnow)
                        DBSession.add(n)
                        DBSession.flush()
                    except Exception as e:
                        log.error('Error creating new node node_name={0},unique_id={1},exception={2}'.format(node_name, unique_id, e))
                        raise
                else:
                    try:
                        log.info('Updating node: {0}'.format(unique_id))
                        n = DBSession.query(Node).filter(Node.unique_id==unique_id).one()
                        n.node_name = node_name
                        n.hardware_profile_id = hardware_profile_id
                        n.operating_system_id = operating_system_id
                        n.uptime = uptime
                        n.updated_by=au['user_id']
                        DBSession.flush()
                    except Exception as e:
                        log.error('Error updating node node_name={0},unique_id={1},exception={2}'.format(node_name, unique_id, e))
                        raise
            else:

                # Manually created node via the client.
                try:
                    node_name = payload['node_name']
                    status_id = payload['node_status_id']
                    utcnow = datetime.utcnow()

                    log.info('Manually creating new node: {0}'.format(node_name))

                    # FIXME: unique_id, hardware_profile, and operating_system?
                    n = Node(node_name=node_name,
                             status_id=status_id,
                             updated_by=au['user_id'],
                             created=utcnow,
                             updated=utcnow)
                    DBSession.add(n)
                    DBSession.flush()
                except Exception as e:
                    log.error('Error creating new node node_name={0},status_id={1},exception={2}'.format(node_name, status_id, e))
                    raise

            return n

        if request.matchdict['id']:

            node_id = request.matchdict['id']
            payload = request.json_body

            s = ''
            for k,v in payload.items():
                s+='{0}={1},'.format(k, v)

#            if 'status' in payload.keys():
#
#                # FIXME: This
#                uri = '/api/statuses'
#                data = {'status_name': payload['status']}
#                status = _api_get(request, uri, data)
#                status_id = status['status_id']
#
#                # FIXME: vs. this ???
#                # status_id = Status.get_status_id(payload['status'])
#
#                log.info('status_id: {0}'.format(status_id))

            log.info('Updating node_id: {0} params: {1}'.format(node_id, s.rstrip(',')))

            q = DBSession.query(Node).filter(Node.node_id==node_id)
            n = q.one()

            # FIXME: Do we want to limit anything here? Keys that don't exist will 
            # be ignored, keys that can't be set with throw an error. Doesn't
            # feel right though to just accept what's put to the endpoint.
            for k,v in payload.items():
                setattr(n ,k, v)

            n.updated_by=au['user_id']
            DBSession.flush()

    except Exception, e:
        log.error('Error with node API! exception: {0}'.format(e))
        return Response(str(e), content_type='application/json', status_int=500)


@view_config(route_name='api_nodes', permission='api_write', request_method='DELETE', renderer='json')
def api_nodes_delete(request):

    au = get_authenticated_user(request)

    try:
        payload = request.json_body

        if request.path == '/api/nodes':

            # FIXME: This is ugly
            node_name = payload.get('node_name', None)
            unique_id = payload.get('unique_id', None)
#                unique_id = payload['unique_id'] or None

            if not any((node_name, unique_id)):
                log.error('You must specify one of node_name or unique_id')
                return Response(content_type='application/json', status_int=400)
            else:
                try:
                    log.info('Checking for node_name={0},unique_id={1}'.format(node_name, unique_id))
                    q = DBSession.query(Node)

                    if node_name:
                        q = q.filter(Node.node_name==node_name)
                    if unique_id:
                        q = q.filter(Node.unique_id==unique_id)
                    q.one()
                except NoResultFound, e:
                    return Response(content_type='application/json', status_int=404)

                else:
                    try:
                        # FIXME: Need auditing
                        log.info('Deleting node_name={0},unique_id={1}'.format(node_name, unique_id))
                        n = DBSession.query(Node)
                        if node_name:
                            n = n.filter(Node.node_name==node_name)
                        if unique_id:
                            n = n.filter(Node.unique_id==unique_id)
                        n = n.one()
                        DBSession.delete(n)
                        DBSession.flush()
                    except Exception, e:
                        log.info('Error deleting node_name={0},unique_id={1}'.format(node_name, unique_id))
                        raise

                return n

    except Exception, e:
        log.error('Error with node API! exception: {0}'.format(e))
        raise
        return Response(str(e), content_type='application/json', status_int=500)

