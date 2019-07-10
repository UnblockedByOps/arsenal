'''Arsenal client Statuses class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class Statuses(ArsenalInterface):
    '''The arsenal client Statuses class.'''

    def __init__(self, **kwargs):
        super(Statuses, self).__init__(**kwargs)
        self.uri = '/api/statuses'

    # Overridden methods
    def search(self, params=None):
        '''Search for statuses.

        Usage:

        >>> params = {
        ...   'name': 'inservice',
        ...   'exact_get': True,
        ... }
        >>> Statuses.search(params)

        Args:
            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Statuses, self).search(params=params)

    def create(self, params):
        '''Create a status.

        Args:
            params (dict): A dictionary of url parameters for the request. The
                following keys arew required:
                    name
                    description

        Usage:

        >>> params = {
        ...   'description': 'Instances that have been spun down that will be spun up on demand.',
        ...   'name': 'hibernating'
        ... }
        >>> Statuses.create(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Statuses, self).create(params)

    def update(self, params):
        '''Update a status.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only these params are updatable from this action.

        >>> params = {
        ...   'description': 'Instances that have been spun down that will be spun up on demand.',
        ...   'name': 'hibernating'
        ... }
        >>> Statuses.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Statuses, self).update(params)

    def delete(self, params):
        '''Delete a status object from the server.

        Args:

            params: A status dictionary to delete. Must contain the
                status id and name.

        Usage:

        >>> params = {
        ...   'id': 4,
        ...   'name': 'hibernating'
        ... }
        >>> Statuses.delete(params)
        '''

        LOG.info('Deleting status id: {0} name: {1}'.format(params['id'],
                                                            params['name']))
        return super(Statuses, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for statuses.'''
        return super(Statuses, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single status by it's name.

        Args:
            name (str): A string representing the status name you wish to find.
        '''
        return super(Statuses, self).get_by_name(name)

    # Custom methods
    def assign(self, status_name, object_type, results):
        '''Set the status of one or more nodes or data_centers.

        Args:

            status_name (string): The name of the status you wish to set the
                node(s) to.
            object_type (str): A string representing the object_type to assign the
                status to. One of nodes or data_centers.
            results    : The nodes or data_centers from the results
                of <Class>.search() to assign the status to.

        Usage:

            >>> Status.assign('inservice', 'nodes' <search() results>)
            <Response [200]>
        '''

        try:
            status = self.get_by_name(status_name)
        except NoResultFound:
            return None

        action_ids = [result['id'] for result in results]

        LOG.info('Assigning status: {0}'.format(status['name']))

        for result in results:
            LOG.info('  {0}: {1}'.format(object_type, result['name']))

        data = {
            object_type: action_ids
        }

        uri = '/api/statuses/{0}/{1}'.format(status['id'], object_type)
        return self.api_conn(uri, data, method='put')
