'''Arsenal client DataCenters class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface

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

        LOG.info('Deleting data_center name: {0}'.format(params['name']))
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
    # TBD
