'''Arsenal client interface'''
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
import logging
import json
from abc import ABCMeta
from abc import abstractmethod

import requests
from arsenalclient.exceptions import NoResultFound
from arsenalclient.authorization import Authorization

LOG = logging.getLogger(__name__)

logging.VERBOSE = 11
logging.addLevelName(logging.VERBOSE, "VERBOSE")
def verbose(self, message, *args, **kws):
    '''Set custom logging level for more logging information than info but less
    than debug.'''

    if self.isEnabledFor(logging.VERBOSE):
        # pylint: disable=W0212
        self._log(logging.VERBOSE, message, args, **kws)
logging.Logger.verbose = verbose


class ArsenalInterface(object):
    '''The arsenal client interface.

    This is the abstract base class that all the interface clasees are based
    on. It handles Authorization and http calls to the API, as well as implements the
    default abstract methods that must be overrideen by the child classes.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):

        self.uri = None

        self.session = requests.session()
        self.cookies = None

        self.settings = kwargs['settings']
        self.authorization = Authorization(api_host=self.settings.api_host,
                                           api_protocol=self.settings.api_protocol,
                                           cookie_file=self.settings.cookie_file,
                                           user_login=self.settings.user_login,
                                           user_password=self.settings.user_password,
                                           verify_ssl=self.settings.verify_ssl)

    @staticmethod
    def check_response_codes(resp, log_success=True):
        '''Checks the response codes and logs appropriate messaging for the client.

        Args:
            resp: A response object from the requests package.

        Returns:
            Json from response if successful, json formatted response code otherwise.
        '''

        try:
            results = resp.json()
            if resp.status_code == 200:
                if log_success:
                    LOG.info('Command successful.')
            else:
                LOG.warn('{0}: {1}'.format(results['http_status']['code'],
                                           results['http_status']['message']))
            LOG.debug('Returning json...')
            return results
        except ValueError:
            LOG.debug('Json decode failed, falling back to manual json response...')
            my_resp = {
                'http_status': {
                    'code': resp.status_code,
                    'message': resp.reason,
                }
            }
            LOG.warn('{0}: {1}'.format(resp.status_code,
                                       resp.reason))
            return my_resp

    def api_conn(self, uri, data=None, method='get', log_success=True):
        ''' Manages http requests to the API.

        Usage:

            >>> data = {
            ...     'unique_id': '12345'
            >>> }
            >>> api_conn('/api/nodes', data)
            <{json object}>
            >>> api_conn('/api/invalid', data)
            <Response 404>
            >>> api_conn('/api/nodes/1')
            <{json object}>
            >>> api_conn('/api/nodes', data, 'put')
            <{json object}>
            >>> api_conn('/api/nodes', data, 'delete')
            <{json object}>

        Args:

            data (dict): A dict of paramters to send with the http request.
            method (str): The http method to use. Valid choices are:
                delete
                get
                put

        Returns:
            check_response_codes()
        '''

        headers = {'content-type': 'application/json'}

        api_url = '{0}://{1}{2}'.format(self.settings.api_protocol,
                                        self.settings.api_host,
                                        uri)

        try:
            if method == 'put':

                self.authorization.get_cookie_auth()

                LOG.verbose('PUT API call to endpoint: {0}'.format(api_url))
                LOG.verbose('PUT params: \n{0}'.format(json.dumps(data,
                                                                  indent=2,
                                                                  sort_keys=True)))

                resp = self.session.put(api_url,
                                        verify=self.settings.verify_ssl,
                                        cookies=self.authorization.cookies,
                                        headers=headers,
                                        json=data)

                # re-auth if our cookie is invalid/expired
                if resp.status_code == 401:
                    LOG.debug('Recieved 401 from api, re-authenticating...')
                    self.authorization.authenticate()
                    resp = self.session.put(api_url,
                                            verify=self.settings.verify_ssl,
                                            cookies=self.authorization.cookies,
                                            headers=headers,
                                            json=data)

                return self.check_response_codes(resp)

            elif method == 'delete':

                self.authorization.get_cookie_auth()

                LOG.verbose('DELETE API call to endpoint: {0}'.format(api_url))
                LOG.verbose('DELETE params: \n{0}'.format(json.dumps(data,
                                                                     indent=2,
                                                                     sort_keys=True,)))

                resp = self.session.delete(api_url,
                                           verify=self.settings.verify_ssl,
                                           cookies=self.authorization.cookies,
                                           headers=headers,
                                           json=data)

                # re-auth if our cookie is invalid/expired
                if resp.status_code == 401:
                    LOG.debug('Recieved 401 from api, re-authenticating...')
                    self.authorization.authenticate()
                    resp = self.session.delete(api_url,
                                               verify=self.settings.verify_ssl,
                                               cookies=self.authorization.cookies,
                                               headers=headers,
                                               json=data)

                return self.check_response_codes(resp)

            else:
                LOG.verbose('GET API call to endpoint: {0}'.format(api_url))
                LOG.verbose('GET params: \n{0}'.format(json.dumps(data,
                                                                  indent=2,
                                                                  sort_keys=True,)))

                resp = self.session.get(api_url,
                                        verify=self.settings.verify_ssl,
                                        params=data)

                return self.check_response_codes(resp, log_success=log_success)

        except requests.exceptions.ConnectionError:
            LOG.error('Unable to connect to server: {0}'.format(self.settings.api_host))
            raise

    @abstractmethod
    def search(self, params=None):
        '''Search for objects in the API.

        Args:

        params (dict): a dictionary of url parameters for the request.

        Returns:

        A json response from check_response_codes(().
        '''

        LOG.verbose('Searching for {0}...'.format(self.uri.split('/')[-1]))

        resp = self.api_conn(self.uri, params, log_success=False)

        LOG.debug('Results are: {0}'.format(json.dumps(resp,
                                                       indent=2,
                                                       sort_keys=True)))
        if not resp['results']:
            LOG.info('No results found for search.')

        return resp

    @abstractmethod
    def create(self, params):
        '''Create a resource.'''
        LOG.info('Creating {0}...'.format(self.uri.split('/')[-1]))
        resp = self.api_conn(self.uri, params, method='put', log_success=False)
        return resp

    @abstractmethod
    def update(self, params):
        '''Update a resource.'''
        LOG.info('Updating {0}...'.format(self.uri.split('/')[-1]))
        resp = self.api_conn(self.uri, params, method='put', log_success=False)
        return resp

    @abstractmethod
    def delete(self, params):
        '''Delete a resource.'''
        resource_uri = '{0}/{1}'.format(self.uri, params['id'])
        LOG.info('Deleting {0}...'.format(resource_uri))
        resp = self.api_conn(resource_uri, method='delete')
        return resp

    @abstractmethod
    def get_audit_history(self, results):
        '''Retrieve audit history for a list of search results. Returns an
        updated list with audit history attached.'''

        audit_base_uri = self.uri + '_audit'
        resp = []
        for obj in results:
            my_audit = self.api_conn('{0}/{1}'.format(audit_base_uri, obj['id']),
                                     log_success=False)
            obj['audit_history'] = my_audit['results']
            resp.append(obj)

        return resp

    @abstractmethod
    def get_by_name(self, name):
        '''Retrieve a unique resource by name. Returns an single resource if
        one is found, raised NoResultFound if no result, raises a
        RuntimeError otherwise.'''

        LOG.verbose('Searching for single {0} by name...'.format(self.uri.split('/')[-1]))
        params = {
            'name': name,
            'exact_get': True,
        }

        resp = self.api_conn(self.uri, params, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'No result found: {0}'.format(name)
            LOG.warn(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found: {0}'.format(name)
            LOG.warn(msg)
            raise RuntimeError(msg)

        return resource
