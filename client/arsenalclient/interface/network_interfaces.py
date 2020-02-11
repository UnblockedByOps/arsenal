'''Arsenal client NetworkInterfaces class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class NetworkInterfaces(ArsenalInterface):
    '''The arsenal client NetworkInterfaces class.'''

    def __init__(self, **kwargs):
        super(NetworkInterfaces, self).__init__(**kwargs)
        self.uri = '/api/network_interfaces'

    # Overridden methods
    def search(self, params=None):
        '''Search for network_interfaces.

        Usage:

        >>> params = {
        ...   'unique_id': '00:11:22:aa:bb:cc',
        ...   'exact_get': True,
        ... }
        >>> NetworkInterfaces.search(params)

        Args:
            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(NetworkInterfaces, self).search(params=params)

    def create(self, params):
        '''We do not allow network_interfaces to be created manually.'''
        pass

    def update(self, params):
        '''We do not allow network_interfaces to be updated.'''
        pass

    def delete(self, params):
        '''We do not allow network_interfaces to be deleted.'''
        pass

    def get_audit_history(self, results):
        '''Get the audit history for network_interfaces.'''
        return super(NetworkInterfaces, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a network_interface tag by it's name. This is not possible as
        network_interfaces do not have unique names. Use
        NetworkInterfaces.get_by_unique_id() instead.
        '''
        pass

    # Custom methods
    def get_by_unique_id(self, unique_id):
        '''Get a network_interface from the server based on it's unique_id.'''

        LOG.debug('Searching for network_interface unique_id: {0}'.format(unique_id))

        data = {
            'unique_id': unique_id,
            'exact_get': True,
        }

        resp = self.api_conn('/api/network_interfaces', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'network_interface not found: {0}'.format(unique_id)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found: {0}'.format(unique_id)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource
