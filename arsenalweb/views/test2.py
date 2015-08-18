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
from sqlalchemy.sql import func
from sqlalchemy import or_
from sqlalchemy import desc
from sqlalchemy.sql import label
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    log,
    )
from arsenalweb.models import (
    DBSession,
    )

@view_config(route_name='test2', permission='view', renderer='arsenalweb:templates/test2.pt')
@view_config(route_name='test2', permission='api_write', request_method='GET', request_param='format=json', renderer='json')
@view_config(route_name='test2', permission='view', request_param='format=xml', renderer='xml')
def view_test2(request):
    page_title_type = 'objects_'
    page_title_name = 'Statuses'
    au = get_authenticated_user(request)

    params = {'format': None,
              'type': 'vir',
             }
    for p in params:
        try:
            params[p] = request.params[p]
        except:
            pass

    format = params['format']
    type = params['type']

    if format == 'json' or format == 'xml':
        return {'Hello':'world'}

    if type == 'ec2':
        host = 'aws1prdtcw1.opsprod.ctgrd.com'
        uniq_id = 'i-303a6c4a'
        ng = 'tcw'
        vhost = 'aws1'
    elif type == 'rds':
        host = 'aws1devcpd1.csqa.ctgrd.com'
        uniq_id = 'aws1devcpd1.cltftmkcg4dd.us-east-1.rds.amazonaws.com'
        ng = 'none'
        vhost = 'aws1'
    else:
        host = 'vir1prdpaw1.prod.cs'
        uniq_id = '6A:37:2A:68:E1:B0'
        ng = 'paw'
        vhost = 'vir1prdxen41.prod.cs'

    return {'layout': site_layout('max'),
            'page_title_type': page_title_type,
            'page_title_name': page_title_name,
            'au': au,
#            'results': results,
            'type': type,
            'host': host,
            'uniq_id': uniq_id,
            'ng': ng,
            'vhost': vhost,
           }

