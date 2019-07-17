'''Arsenal client PhysicalRacks class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class PhysicalRacks(ArsenalInterface):
    '''The arsenal client PhysicalRacks class.'''

    def __init__(self, **kwargs):
        super(PhysicalRacks, self).__init__(**kwargs)
        self.uri = '/api/physical_racks'

    # Overridden methods
    def search(self, params=None):
        '''Search for physical_racks.

        Usage:

        >>> params = {
        ...   'name': 'R500',
        ...   'exact_get': True,
        ... }
        >>> PhysicalRacks.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalRacks, self).search(params)

    def create(self, params):
        '''Create a new physical_rack.

        Args:

        params (dict): A dictionary with the following attributes:

        name : The name of the physical_rack you wish to create.
        physical_location : The name of the physical_location the
            physical_rack you wish to create will be in.

        Usage:

        >>> params = {
        ...     'name': 'R500',
        ...     'physical_location': 'TEST DC SCIF 1',
        ... }
        >>> PhysicalRacks.create(params)
        <Response [200]>
        '''

        return super(PhysicalRacks, self).create(params)

    def update(self, params):
        '''Update a physical_rack.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only the params in the example are updatable from this action.

        >>> params = {
        ...     'name': 'R500',
        ...     'physical_location': 'TEST DC SCIF 2',
        ... }
        >>> PhysicalRacks.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalRacks, self).update(params)

    def delete(self, params):
        '''Delete a physical_rack object from the server.

        Args:

            params: A physical_rack dictionary to delete. Must contain the
                physical_rack id, and name.

        Usage:

        >>> params = {
        ...     'id': 1,
        ...     'name': 'R500',
        ... }
        >>> PhysicalRacks.delete(params)
        '''

        return super(PhysicalRacks, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for physical_racks.'''
        return super(PhysicalRacks, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single physical_rack by it's name. This is not possible as
        physical_racks are not unique by name alone. Use PhysicalRacks.get_by_name_location()
        instead.
        '''
        pass

    # Custom methods
    def get_by_name_location(self, name, location):
        '''Get a single physical_rack by it's name and location.'''

        LOG.debug('Searching for physical_rack by name: {0} location: {1}'.format(name,
                                                                                  location))
        data = {
            'name': name,
            'physical_location.name': location,
        }

        resp = self.api_conn('/api/physical_racks', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'Physical Rack not found, name: {0} location: {1}'.format(name,
                                                                            location)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found, name: {0} location: {1}'.format(name,
                                                                               location)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource
