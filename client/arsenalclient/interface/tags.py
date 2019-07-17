'''Arsenal client Tags class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class Tags(ArsenalInterface):
    '''The arsenal client Tags class.'''

    def __init__(self, **kwargs):
        super(Tags, self).__init__(**kwargs)
        self.uri = '/api/tags'

    # Overridden methods
    def search(self, params=None):
        '''Search for tags.

        Usage:

        >>> params = {
        ...     'name': 'my_tag',
        ...     'exact_get': True,
        ... }
        >>> Tags.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(Tags, self).search(params)

    def create(self, params):
        '''Create a new tag.

        Args:

        params (dict): A dictionary with the following attributes:

        tag_name : The name of the tag you wish to create.
        tag_value: The value of the tag you wish to create.

        Usage:

        >>> params = {
        ...     'name': 'meaning',
        ...     'value': 42,
        ... }
        >>> Tags.create(params)
        <Response [200]>
        '''

        return super(Tags, self).create(params)

    def update(self, params):
        '''Update a tag. There is nothing to update with tags as every field
        must be unique.'''
        pass

    def delete(self, params):
        '''Delete a tag object from the server.

        Args:

            params: A tag dictionary to delete. Must contain the
                tag id, name, and value.

        Usage:

        >>> params = {
        ...    'id': 1,
        ...    'name': 'my_tag',
        ...    'value': 'my_string',
        ... }
        >>> Tags.delete(params)
        '''

        return super(Tags, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for tags.'''
        return super(Tags, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single tag by it's name. This is not possible as a tag's
        uniqueness is determined by both it's name and value. Use
        Tags.get_by_name_value() instead.
        '''
        pass

    # Custom methods
    def get_by_name_value(self, name, value):
        '''Get a tag from the server based on it's name and value.'''

        LOG.debug('Searching for tag name: {0} value: {1}'.format(name,
                                                                  value))
        data = {
            'name': name,
            'value': value,
            'exact_get': True,
        }

        resp = self.api_conn('/api/tags', data, log_success=False)
        LOG.debug('Results are: {0}'.format(resp))

        try:
            resource = resp['results'][0]
        except IndexError:
            msg = 'Tag not found: {0}={1}'.format(name, value)
            LOG.info(msg)
            raise NoResultFound(msg)
        if len(resp['results']) > 1:
            msg = 'More than one result found: {0}'.format(name)
            LOG.error(msg)
            raise RuntimeError(msg)

        return resource

    def _manage_assignments(self, name, value, object_type, results, api_method):
        '''Assign or de-assign a tag to a list of node, node_group, or
        data_center dictionaries.'''

        action_names = []
        action_ids = []
        msg = 'Assigning'
        if api_method == 'delete':
            msg = 'De-assigning'

        for action_object in results:
            action_names.append(action_object['name'])
            action_ids.append(action_object['id'])

        try:
            this_tag = self.get_by_name_value(name, value)
        except NoResultFound:
            if api_method == 'delete':
                LOG.debug('Tag not found, nothing to do.')
                return
            else:
                params = {
                    'name': name,
                    'value': value,
                }
                resp = self.create(params)
                this_tag = resp['results'][0]

        LOG.info('{0} tag: {1}={2}'.format(msg,
                                           this_tag['name'],
                                           this_tag['value']))
        for action_name in action_names:
            LOG.info('  {0}: {1}'.format(object_type, action_name))

        data = {
            object_type: action_ids
        }

        try:
            uri = '/api/tags/{0}/{1}'.format(this_tag['id'], object_type)
            resp = self.api_conn(uri, data, method=api_method)
        except:
            raise

        return resp

    def assign(self, name, value, object_type, results):
        '''Assign a tag to one or more nodes, node_groups, or data_centers.

        Args:

        name (str)   : The name of the tag to assign to the <Class>.search() results.
        value (str)  : The value of the tag to assign to the <Class>.search() results.
        object_type (str): A string representing the object_type to assign the
            tag to. One of nodes, node_groups or data_centers.
        results    : The nodes, node_groups, or data_centers from the results
            of <Class>.search() to assign the tag to.

        Usage:

        >>> Tags.assign('meaning', 42, 'nodes', <search results>)
        <json>
        '''

        return self._manage_assignments(name, value, object_type, results, 'put')

    def deassign(self, name, value, object_type, results):
        '''De-assign a tag from one or more nodes, node_groups, or data_centers.

        Args:

        name (str)   : The name of the tag to deassign to the <Class>.search() results.
        value (str)  : The value of the tag to deassign to the <Class>.search() results.
        object_type (str): A string representing the object_type to deassign the
            tag to. One of nodes, node_groups or data_centers.
        results    : The nodes, node_groups, or data_centers from the results
            of <Class>.search() to deassign the tag from.

        Usage:

        >>> Tags.deassign('meaning', 42, 'nodes', <search results>)
        <json>
        '''

        return self._manage_assignments(name, value, object_type, results, 'delete')
