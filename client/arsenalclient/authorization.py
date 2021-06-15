'''Arsenal Authorization class.'''
#
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
import os
import logging
import getpass
import ast
import requests
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except (ImportError, AttributeError):
    pass

LOG = logging.getLogger(__name__)

# requests is chatty
logging.getLogger("requests").setLevel(logging.WARNING)
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass

def check_root():
    '''Check and see if we're running as root. Returns True or False.'''

    if not os.geteuid() == 0:
        LOG.error('This command must be run as root.')
        return False
    return True


class Authorization(object):
    '''The Arsenal Authorization class.

        Usage::

            >>> from arsenalclient.authorization import Authorization
            >>> params = {
                ...     'cookie_file': '/home/abandt/.arsenal_cookie.txt',
                ...     'user_login': 'abandt',
                ... }
            >>> auth = Authorization(**params)

        Required Args:
            cookie_file: A string that is the path to the cookie file to use. This
                should map to a file in the homedir of the user.
            user_login : A string that is the user's login name.

        Optional Args:
            api_host     : A string that is the name of the Arsenal server. Default
                value is 'arsenal'.
            api_protocol : A string that is the protocol version to use. Valid
                values are 'https' (default) or 'http'.
            user_password: A string that is the user's password.
            verify_ssl   : Whether or not to verify the ssl connection to the Arsenal
                server. Defaults to True.
    '''

    def __init__(self,
                 api_host='arsenal',
                 api_protocol='https',
                 verify_ssl=True,
                 **kwargs
                ):

        self.session = requests.session()
        self.cookies = None
        self.api_protocol = api_protocol
        self.api_host = api_host
        self.cookie_file = kwargs.get('cookie_file')
        self.user_login = kwargs.get('user_login')
        self.user_password = kwargs.get('user_password')
        self.verify_ssl = verify_ssl

    def get_cookie_auth(self):
        '''Gets cookies from cookie file or authenticates if no cookie file is
        present.

        Returns:
            A dict of all cookies if successful, raises an exception otherwise.
        '''

        try:
            self.read_cookie()
            if not self.cookies:
                self.authenticate()
            else:
                self.cookies = ast.literal_eval(self.cookies)

        except Exception as ex:
            LOG.error('Failed to evaluate cookies: {0}'.format(repr(ex)))
            raise

    def read_cookie(self):
        '''Reads cookies from cookie file.

        Returns:
            A dict of all cookies if cookie_file is present, None otherwise.
        '''

        LOG.debug('Checking for cookie file: {0}'.format(self.cookie_file))

        if os.path.isfile(self.cookie_file):
            LOG.debug('Cookie file found: {0}'.format(self.cookie_file))
            with open(self.cookie_file, 'r') as contents:
                self.cookies = contents.read()
        else:
            LOG.debug('Cookie file does not exist: {0}'.format(self.cookie_file))

    def write_cookie(self, cookies):
        '''Writes cookies to cookie file.

        Returns:
            True if successful, False otherwise.
        '''

        LOG.info('Writing cookie file: {0}'.format(self.cookie_file))

        try:
            cookie_dict = dict(cookies)
            with open(self.cookie_file, "w") as cookie_file:
                cookie_file.write(str(cookie_dict))
            os.chmod(self.cookie_file, 0o600)

        except Exception as ex:
            LOG.error('Unable to write cookie: '
                      '{0}'.format(self.cookie_file))
            LOG.error('Exception: {0}'.format(repr(ex)))
            raise

    def authenticate(self):
        '''Prompts for user password and authenticates against the API. Writes
        response cookies to file for later use.

        Returns:
            A dict of all cookies if successful, None otherwise.
        '''

        if self.user_login == 'read_only':
            LOG.error('Write access denied for read_only user.')
            return None
        else:
            LOG.info('Authenticating login: {0}'.format(self.user_login))

            # Kaboom password is exposed on dev systems where others have root,
            # thus insecurable. This may change in the future.
            if self.user_login == 'kaboom':
                password = 'password'
            elif getattr(self, 'user_password'):
                password = self.user_password
            else:
                password = getpass.getpass('password: ')

            try:
                payload = {
                    'form.submitted': True,
                    'api.client': True,
                    'return_url': '/api',
                    'login': self.user_login,
                    'password': password
                }
                resp = self.session.post(self.api_protocol
                                         + '://'
                                         + self.api_host
                                         + '/login', data=payload,
                                         verify=self.verify_ssl)

                resp.raise_for_status()
                LOG.debug('Authentication successful for user: {0}'.format(self.user_login))

                self.cookies = self.session.cookies.get_dict()
                LOG.debug('Resp is: %s', resp)
                LOG.debug('Resp dir is: %s', dir(resp))
                LOG.debug('Resp headers: %s', resp.headers)
                LOG.debug('Resp cookies: %s', dir(resp.cookies))
                LOG.debug('Cookies are: %s', self.session.cookies)
                LOG.debug('Cookies are: %s', self.cookies)
                try:
                    self.write_cookie(self.cookies)
                except Exception as ex:
                    LOG.error('Exception: {0}'.format(repr(ex)))
                    raise

            except Exception as ex:
                LOG.error('Exception: {0}'.format(repr(ex)))
                LOG.error('Authentication failed')
                raise
