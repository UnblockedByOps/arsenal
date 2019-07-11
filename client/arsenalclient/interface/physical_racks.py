'''Arsenal client PhysicalRacks class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface

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
        ...   'serial_number': 'AA11BB22CC34',
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

        serial_number : The serial_number of the physical_rack you wish to create.

        Usage:

        >>> params = {
        ...     'serial_number': 'AA11BB22CC34',
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
        ...     'serial_number': 'AA11BB22CC34',
        ...     'physical_elevation': 7,
        ...     'physical_location': 'SCIF 4',
        ...     'physical_rack': 'R200',
        ...     'hardware_profile': 'HP ProLiant DL360 Gen9',
        ...     'oob_ip_address': '10.0.0.1',
        ...     'oob_mac_address': 'aa:bb:cc:11:22:33',
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
        ...    'id': 1,
        ...    'serial_number': 'AA11BB22CC34',
        ... }
        >>> PhysicalRacks.delete(params)
        '''

        LOG.info('Deleting physical_rack serial_number: {0}'.format(params['serial_number']))
        return super(PhysicalRacks, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for physical_racks.'''
        return super(PhysicalRacks, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single physical_rack by it's name. This is not possible as
        physical_devices don't have a name. Use PhysicalRacks.get_by_serial_number()
        instead.
        '''
        pass

    # Custom methods
    # TBD
