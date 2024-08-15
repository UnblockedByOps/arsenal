'''Arsenal client DataCenters class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class DataCenters(ArsenalInterface):
    '''The arsenal client DataCenters class.'''

    def __init__(self, **kwargs):
        super(DataCenters, self).__init__(**kwargs)
        self.uri = '/api/data_centers'

    # Overridden methods
    def search(self, params=None):
        '''Search for data_centers.

        Usage:

        >>> params = {
        ...   'name': 'my_data_center',
        ...   'exact_get': True,
        ... }
        >>> DataCenters.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(DataCenters, self).search(params)

    def create(self, params):
        '''Create a new data_center.

        Args:

        params (dict): A dictionary with the following attributes:

        name : The name of the data_center you wish to create.

        Usage:

        >>> params = {
        ...     'name': 'my_data_center1',
        ... }
        >>> DataCenters.create(params)
        <Response [200]>
        '''

        return super(DataCenters, self).create(params)

    def update(self, params):
        '''There is nothing to update with data_centers. Use
        Statuses.assign() to set the status of a data_center.'''
        pass

    def delete(self, params):
        '''Delete a data_center object from the server.

        Args:

            params: A data_center dictionary to delete. Must contain the
                data_center id, and name.

        Usage:

        >>> params = {
        ...    'id': 1,
        ...    'name': 'my_data_center',
        ... }
        >>> DataCenters.delete(params)
        '''

        return super(DataCenters, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for data_centers.'''
        return super(DataCenters, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single data_center by it's name.

        Args:
            name (str): A string representing the data_center name you wish to find.
        '''
        return super(DataCenters, self).get_by_name(name)

    # Custom methods
    def assign(self, data_center_name, object_type, results):
        '''Set the data_center of one or more physical_locations.

        Args:

            data_center_name (string): The name of the data_center you wish to set the
                physical_location(s) to.
            object_type (str): A string representing the object_type to assign the
                data_center to. Only physical_locations are currently supported.
            results    : The physical_locations from the results
                of <Class>.search() to assign the data_center to.

        Usage:

            >>> DataCenters.assign('las2', 'physical_locations', <search() results>)
            <Response [200]>
        '''

        try:
            data_center = self.get_by_name(data_center_name)
        except NoResultFound:
            return None

        action_ids = [result['id'] for result in results]

        LOG.info('Assigning data_center: %s', data_center['name'])

        for result in results:
            try:
                LOG.info('  %s: %s', object_type, result['name'])
            # physical_devices don't have a name attribute
            except KeyError:
                LOG.info('  %s: %s', object_type, result['serial_number'])

        data = {
            object_type: action_ids
        }

        uri = "/api/data_centers/{0}/{1}".format(data_center['id'], object_type)
        return self.api_conn(uri, data, method='put')
