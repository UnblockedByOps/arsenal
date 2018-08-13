'''Arsenal user UI.'''
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
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from passlib.hash import sha512_crypt
from arsenalweb.views import (
    get_authenticated_user,
    site_layout,
    )
from arsenalweb.models.common import (
    DBSession,
    User,
    )

LOG = logging.getLogger(__name__)

@view_config(route_name='user', permission='view', renderer='arsenalweb:templates/user.pt')
def view_user(request):
    '''Handle requests for user UI route.'''

    auth_user = get_authenticated_user(request)
    page_title_type = 'user/'
    page_title_name = 'User Data'
    change_pw = False
    perpage = 1
    offset = 1
    total = 1

    if 'user.submitted' in request.POST:
        email_address = request.POST['email_address']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']

        # Need some security checking here
        if email_address != auth_user['login']:
            print "Naughty monkey"
        else:
            # Update
            LOG.info('UPDATE: email_address=%s,first_name=%s,last_name=%s,password=%s'
                     % (email_address,
                        first_name,
                        last_name,
                        'pass'))
            try:
                user = DBSession.query(User).filter(User.user_name==email_address).one()
                user.first_name = first_name
                user.last_name = last_name
                if password:
                    LOG.info('Changing password for: %s' % email_address)
                    salt = sha512_crypt.genconfig()[17:33]
                    encrypted_password = sha512_crypt.encrypt(password, salt=salt)
                    user.salt = salt
                    user.password = encrypted_password
                    DBSession.flush()
                    return_url = '/logout?message=Your password has been changed successfully. Log in again.'
                    return HTTPFound(return_url)

                DBSession.flush()

            except Exception, e:
                pass
                LOG.info("%s (%s)" % (Exception, e))

    # Get the changes
    auth_user = get_authenticated_user(request)
    subtitle = auth_user['first_last']

    column_selectors = []

    return {
        'au': auth_user,
        'change_pw': change_pw,
        'column_selectors': column_selectors,
        'layout': site_layout('max'),
        'offset': offset,
        'page_title_name': page_title_name,
        'page_title_type': page_title_type,
        'perpage': perpage,
        'subtitle': subtitle,
        'total': total,
    }
