'''Arsenal client HardwareProfiles class.'''
import logging
from arsenalclient.interface.arsenal_interface import ArsenalInterface
from arsenalclient.exceptions import NoResultFound

LOG = logging.getLogger(__name__)

class HardwareProfiles(ArsenalInterface):
    '''The arsenal client HardwareProfiles class.'''

    def __init__(self, **kwargs):
        super(HardwareProfiles, self).__init__(**kwargs)
        self.uri = '/api/hardware_profiles'

    # Overridden methods
    def search(self, params=None):
        '''Search for hardware_profiles.

        Usage:

        >>> params = {
        ...   'name': 'inservice',
        ...   'exact_get': True,
        ... }
        >>> HardwareProfiles.search(params)

        Args:
            params (dict): a dictionary of url parameters for the request.

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(HardwareProfiles, self).search(params=params)

    def create(self, params):
        '''Create a hardware_profiles object manually.

        Not allowed.
        '''
        pass

    def update(self, params):
        '''Update a hardware_profile.

        Args:
            params (dict): A dictionary of url parameters for the request.

        Usage:
            Only these params are updatable from this action.

        >>> params = {
        ...   'name': 'HPE ProLiant DL380 Gen10'
        ...   'rack_color': '#c39bd3',
        ...   'rack_u': '2',
        ... }
        >>> HardwareProfiles.update(params)

        Returns:
            A json response from ArsenalInterface.check_response_codes().
        '''

        return super(HardwareProfiles, self).update(params)

    def delete(self, params):
        '''Delete a hardware_profiles object from the server.

        Not allowed.
        '''
        pass

    def get_audit_history(self, results):
        '''Get the audit history for hardware_profiles.'''
        return super(HardwareProfiles, self).get_audit_history(results)

    def get_by_name(self, name):
        '''Get a single hardware_profile by it's name.

        Args:
            name (str): A string representing the hardware_profile name you wish to find.
        '''
        return super(HardwareProfiles, self).get_by_name(name)

    # Custom methods
