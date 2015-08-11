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
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    log,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    NodeGroup,
    )

def get_api_attribute(request, object_type, model_type):

    objects = {'node': 'Node',
               'node_groups': 'NodeGroup',
    }
                
    resource_id = request.matchdict['id']
    resource = request.matchdict['resource']
    log.info('Querying for {0} attribute={1},url={2}'.format(object_type, resource, request.url))

    try:
        q = DBSession.query('{0}'.format(model_type))
        q = q.filter(getattr(model_type, 'node_group_id') == resource_id)
        print "AFTER AFTER ", q
        q = q.one()
        return { resource: getattr(q, resource) }

#    except (NoResultFound, AttributeError):
#        return Response(content_type='application/json', status_int=404)
    except Exception as e:
        log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
        raise

