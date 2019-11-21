'''Arsenal client NodeGroups class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface

LOG = logging.getLogger(__name__)

class NodeGroups(ArsenalInterface):
    '''The arsenal client NodeGroups class.'''

    def __init__(self, **kwargs):
        super(NodeGroups, self).__init__(**kwargs)
        self.uri = '/api/node_groups'

    # Overridden methods
    def search(self, params=None):
        '''Search for node_groups.

        Usage:

        >>> params = {
        ...   'name': 'my_node_group',
        ...   'exact_get': True,
        ... }
        >>> NodeGroups.search(params)

        Args:

            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(NodeGroups, self).search(params=params)

    def create(self, params):
        '''Create a new node_group.

        Args:

        params (dict): A dictionary with the following attributes:

        name       : The name of the node_group you wish to create.
        owner      : The email address of the owner of the node group.
        description: A text description of the members of this node_group.
        notes_url  : A url to documentation relevant to the node_group.

        Usage:

        >>> params = {
        ...    'name': 'my_node_group',
        ...    'owner': 'email@mycompany.com',
        ...    'description': 'The nodegroup for all the magical servers',
        ...    'notes_url': 'https://somurl.somedomain.com/',
        ... }
        >>> NodeGroups.create(params)
        <Response [200]>
        '''

        return super(NodeGroups, self).create(params)

    def update(self, params):
        '''Update a node_group.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only these params are updatable from this action.

        >>> params = {
        ...    'name': 'my_node_group',
        ...    'owner': 'email@mycompany.com',
        ...    'description': 'The nodegroup for all the magical servers',
        ...    'notes_url': 'https://somurl.somedomain.com/',
        ... }
        >>> NodeGroups.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(NodeGroups, self).update(params)

    def delete(self, params):
        '''Delete a node_group object from the server.

        Args:

            params: A node_group dictionary to delete. Must contain the
                node_group id, and name.

        Usage:

        >>> params = {
        ...    'id': 1,
        ...    'name': 'my_node_group',
        ... }
        >>> NodeGroups.delete(params)
        '''

        return super(NodeGroups, self).delete(params)

    def get_audit_history(self, results):
        '''Get the audit history for node_groups.'''
        return super(NodeGroups, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single node_group by it's name.

        Args:
            name (str): A string representing the node_group name you wish to find.
        '''
        return super(NodeGroups, self).get_by_name(name)


    # Custom methods
    def _manage_assignments(self, node_group, nodes, api_method):
        '''Assign or de-assign a node_group to/from a list of node dictionaries.'''

        node_names = []
        node_ids = []
        msg = 'Assigning'
        if api_method == 'delete':
            msg = 'De-assigning'

        for node in nodes:
            node_names.append(node['name'])
            node_ids.append(node['id'])

        LOG.info('{0} node_group: {1}'.format(msg,
                                              node_group['name']))
        for node in node_names:
            LOG.info('  node: {0}'.format(node))

        data = {
            'nodes': node_ids
        }

        return self.api_conn('/api/node_groups/{0}/nodes'.format(node_group['id']),
                             data,
                             method=api_method)

    def assign(self, name, nodes):
        '''Assign a node_group to one or more nodes.

        Args:

        name (str)  : The name of the node_group to assign to the node search results.
        nodes (list): The list of node dicts from the search results to assign to
            the node_group.

        Usage:

        >>> NodeGroups.node_groups.assign('node_group1', <search results>)
        <json>
        '''

        try:
            node_group = self.get_by_name(name)
            return self._manage_assignments(node_group, nodes, 'put')
        except IndexError:
            pass

    def deassign(self, name, nodes):
        '''De-assign a node_group from one or more nodes.

        Args:

        name (str)  : The name of the node_group to de-assign from the node search results.
        nodes (list): The list of node dicts from the search results to de-assign from
            the node_group.

        Usage:

        >>> NodeGroups.deassign('node_group1', <search results>)
        <json>
        '''

        try:
            node_group = self.get_by_name(name)
            return self._manage_assignments(node_group, nodes, 'delete')
        except IndexError:
            pass

    def deassign_all(self, nodes):
        '''De-assign ALL node_groups from one or more nodes.

        Args:

        nodes (list): The list of node dicts from the search results to de-assign
            from all node_groups.

        Usage:

        >>> NodeGroups.deassign_all(<search results>)
        <json>
        '''

        node_ids = []
        for node in nodes:
            LOG.info('Removing all node_groups from node: {0}'.format(node['name']))
            node_ids.append(node['id'])

        data = {'node_ids': node_ids}

        try:
            resp = self.api_conn('/api/bulk/node_groups/deassign',
                                 data,
                                 method='delete')
        except Exception as ex:
            LOG.error('Command failed: {0}'.format(repr(ex)))
            raise

        return resp
