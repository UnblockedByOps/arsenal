'''Arsenal client PhysicalElevations class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

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
    def get_by_loc_rack_el(self, location, rack, elevation):
        '''Get a single physical_elevation by it's elevation, location and rack.'''

        LOG.debug('Searching for physical_elevation by location: {0} '
                  'rack: {1} elevation: {2}'.format(location, rack, elevation))

        data = {
            'physical_location': location,
            'physical_rack': rack,
            'elevation': elevation,
        }

        resp = self.api_conn('/api/physical_elevations', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'Physical Elevation not found, location: {0} rack: {1} ' \
                   'elevation: {2}'.format(location, rack, elevation)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found, location: {0} rack: {1} ' \
                   'elevation: {2}'.format(location, rack, elevation)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource
