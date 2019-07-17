'''Arsenal client PhysicalLocations class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface

LOG = logging.getLogger(__name__)

class PhysicalLocations(ArsenalInterface):
    '''The arsenal client PhysicalLocations class.'''

    def __init__(self, **kwargs):
        super(PhysicalLocations, self).__init__(**kwargs)
        self.uri = '/api/physical_locations'

    # Overridden methods
    def search(self, params=None):
        '''Search for physical_locations.

        Usage:

        >>> params = {
        ...   'name': 'my_physical_location',
        ...   'exact_get': True,
        ... }
        >>> PhysicalLocations.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalLocations, self).search(params)

    def create(self, params):
        '''Create a new physical_location.

        Args:

        params (dict): A dictionary with the following attributes:

        name : The name of the physical_location you wish to create.

        Usage:

        >>> params = {
        ...     'name': 'my_physical_location1',
        ... }
        >>> PhysicalLocations.create(params)
        <Response [200]>
        '''

        return super(PhysicalLocations, self).create(params)

    def update(self, params):
        '''Update a physical_location.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only the params in the example are updatable from this action.

        >>> params = {
        ...     'name': 'SCIF 1',
        ...     'address_1': '1234 Anywhere Street',
        ...     'address_2': '2nd floor',
        ...     'admin_area': 'NV',
        ...     'city': 'Las Vegas',
        ...     'contact_name': 'Joe Manager',
        ...     'country': 'USA',
        ...     'phone_number': '310 555-1212',
        ...     'postal_code': '91100',
        ...     'provider': 'Switch',
        ... }
        >>> PhysicalLocations.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalLocations, self).update(params)

    def delete(self, params):
        '''Delete a physical_location object from the server.

        Args:

            params: A physical_location dictionary to delete. Must contain the
                physical_location id, and name.

        Usage:

        >>> params = {
        ...    'id': 1,
        ...    'name': 'my_physical_location',
        ... }
        >>> PhysicalLocations.delete(params)
        '''

        return super(PhysicalLocations, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for physical_locations.'''
        return super(PhysicalLocations, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single physical_location by it's name.

        Args:
            name (str): A string representing the physical_location name you wish to find.
        '''
        return super(PhysicalLocations, self).get_by_name(name)

    # Custom methods
    # TBD
