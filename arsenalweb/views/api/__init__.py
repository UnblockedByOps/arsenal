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
import re
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound
from arsenalweb.views import (
    log,
    )
from arsenalweb.models import (
    DBSession,
    Node,
    NodeGroup,
    NodeGroupAssignment,
    Status,
    Tag,
    HardwareProfile,
    OperatingSystem,
    )

def get_api_attribute(request, model_type):

    # Convert camel case to underscore for id mapping.
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    c = a.sub(r' \1', model_type).lower().strip()
    c = c.replace(" ","_") + '_id'

    resource_id = request.matchdict['id']
    resource = request.matchdict['resource']
    log.info('Querying for attribute={0},url={1}'.format(resource, request.url))

    try:
        # FIXME: Something better here than globals?
        q = DBSession.query(globals()[model_type])
        q = q.filter(getattr(globals()[model_type], c) == resource_id)
        q = q.one()
        return { resource: getattr(q, resource) }

    except (NoResultFound, AttributeError):
        return Response(content_type='application/json', status_int=404)
    except Exception as e:
        log.error('Error querying node_group={0},exception={1}'.format(request.url, e))
        raise

