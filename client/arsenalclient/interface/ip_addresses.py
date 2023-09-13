'''Arsenal client IpAddresses class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class IpAddresses(ArsenalInterface):
    '''The arsenal client IpAddresses class.'''

    def __init__(self, **kwargs):
        super(IpAddresses, self).__init__(**kwargs)
        self.uri = '/api/ip_addresses'

    # Overridden methods
    def search(self, params=None):
        '''Search for ip_addresses.

        Usage:

        >>> params = {
        ...   'ip_address': '10.100.100.1',
        ...   'exact_get': True,
        ... }
        >>> IpAddresses.search(params)

        Args:
            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(IpAddresses, self).search(params=params)

    def create(self, params):
        '''We do not allow ip_addresses to be created manually.'''
        pass

    def update(self, params):
        '''We do not allow ip_addresses to be updated.'''
        pass

    def delete(self, params):
        '''We do not allow ip_addresses to be deleted.'''
        pass

    def get_audit_history(self, results):
        '''Get the audit history for ip_addresses.'''
        return super(IpAddresses, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get an ip_addresses by it's name. This is not possible as
        ip_addresses do not have unique names. Use
        IpAddresses.get_by_unique_id() instead.
        '''
        pass

    # Custom methods
    def get_by_unique_id(self, unique_id):
        '''Get a ip_addresses from the server based on it's unique_id.'''

        LOG.debug('Searching for ip_addresses unique_id: {0}'.format(unique_id))

        data = {
            'unique_id': unique_id,
            'exact_get': True,
        }

        resp = self.api_conn('/api/ip_addresses', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'ip_addresses not found: {0}'.format(unique_id)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found: {0}'.format(unique_id)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource
