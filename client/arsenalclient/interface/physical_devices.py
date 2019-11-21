'''Arsenal client PhysicalDevices class.'''
import logging
from arsenalclient.exceptions import NoResultFound
from arsenalclient.interface.arsenal_interface import ArsenalInterface

LOG = logging.getLogger(__name__)

class PhysicalDevices(ArsenalInterface):
    '''The arsenal client PhysicalDevices class.'''

    def __init__(self, **kwargs):
        super(PhysicalDevices, self).__init__(**kwargs)
        self.uri = '/api/physical_devices'

    # Overridden methods
    def search(self, params=None):
        '''Search for physical_devices.

        Usage:

        >>> params = {
        ...   'serial_number': 'AA11BB22CC34',
        ...   'exact_get': True,
        ... }
        >>> PhysicalDevices.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalDevices, self).search(params)

    def create(self, params):
        '''Create a new physical_device.

        Args:

        params (dict): A dictionary with the following attributes:

        serial_number : The serial_number of the physical_device you wish to create.

        Usage:

        >>> params = {
        ...     'serial_number': 'AA11BB22CC34',
        ... }
        >>> PhysicalDevices.create(params)
        <Response [200]>
        '''

        return super(PhysicalDevices, self).create(params)

    def update(self, params):
        '''Update a physical_device.

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
        >>> PhysicalDevices.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalDevices, self).update(params)

    def delete(self, params):
        '''Delete a physical_device object from the server.

        Args:

            params: A physical_device dictionary to delete. Must contain the
                physical_device id, and name.

        Usage:

        >>> params = {
        ...    'id': 1,
        ...    'serial_number': 'AA11BB22CC34',
        ... }
        >>> PhysicalDevices.delete(params)
        '''

        return super(PhysicalDevices, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for physical_devices.'''
        return super(PhysicalDevices, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single physical_device by it's name. This is not possible as
        physical_devices don't have a name. Use PhysicalDevices.get_by_serial_number()
        instead.
        '''
        pass

    # Custom methods
    def get_by_serial_number(self, serial_number):
        '''Get a single physical_device from the server based on it's serial_number.'''

        LOG.debug('Searching for physical_device serial_number: {0}'.format(serial_number))
        data = {
            'serial_number': serial_number,
            'exact_get': True,
        }

        resp = self.api_conn('/api/physical_devices', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'Physical Device not found: {0}'.format(serial_number)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found: {0}'.format(serial_number)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource
