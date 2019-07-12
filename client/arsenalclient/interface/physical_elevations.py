'''Arsenal client PhysicalElevations class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface

LOG = logging.getLogger(__name__)

class PhysicalElevations(ArsenalInterface):
    '''The arsenal client PhysicalElevations class.'''

    def __init__(self, **kwargs):
        super(PhysicalElevations, self).__init__(**kwargs)
        self.uri = '/api/physical_elevations'

    # Overridden methods
    def search(self, params=None):
        '''Search for physical_elevations.

        Usage:

        >>> params = {
        ...   'elevation': 2,
        ...   'physical_location': 'TEST DC SCIF 1',
        ...   'exact_get': True,
        ... }
        >>> PhysicalElevations.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalElevations, self).search(params)

    def create(self, params):
        '''Create a new physical_elevation.

        Args:

        params (dict): A dictionary with the following attributes:

        elevation : The number of the physical_elevation you wish to create.
        physical_rack : The name of the physical_rack the
            physical_elevation you wish to create will be in.
        physical_location : The name of the physical_location the
            physical_elevation you wish to create will be in.

        Usage:

        >>> params = {
        ...     'elevation': 10,
        ...     'physical_location': 'TEST DC SCIF 1',
        ...     'physical_rack': 'R500',
        ... }
        >>> PhysicalElevations.create(params)
        <Response [200]>
        '''

        return super(PhysicalElevations, self).create(params)

    def update(self, params):
        '''Update a physical_elevation.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only the params in the example are updatable from this action.

        >>> params = {
        ...     'elevation': 12,
        ...     'physical_location': 'TEST DC SCIF 1',
        ...     'physical_rack': 'R501',
        ... }
        >>> PhysicalElevations.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(PhysicalElevations, self).update(params)

    def delete(self, params):
        '''Delete a physical_elevation object from the server.

        Args:

            params: A physical_elevation dictionary to delete. Must contain the
                physical_elevation id, and name.

        Usage:

        >>> params = {
        ...     'id': 100,
        ...     'elevation': 12,
        ...     'physical_location': 'TEST DC SCIF 1',
        ...     'physical_rack': 'R501',
        ... }
        >>> PhysicalElevations.delete(params)
        '''

        LOG.info('Deleting physical_elevation location: {0} '
                 'rack: {1} elevation: {2}'.format(params['physical_location'],
                                                   params['physical_rack'],
                                                   params['elevation'],))
        return super(PhysicalElevations, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for physical_elevations.'''
        return super(PhysicalElevations, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single physical_elevation by it's name. This is not possible as
        physical_elevations are not unique by name alone. Use
        PhysicalElevations.get_by_loc_rack_el() instead.
        '''
        pass

    # Custom methods
    def get_by_loc_rack_el(self, name, location):
        '''Get a single physical_elevation by it's elevation, location and rack.'''
        # TBD, not sure if we need this yet.
        pass
