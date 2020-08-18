# pylint: disable=too-many-lines
'''Arsenal client library'''
#
#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import sys
import ConfigParser
import logging
from argparse import Namespace
import requests

from arsenalclient.interface.data_centers import DataCenters
from arsenalclient.interface.hardware_profiles import HardwareProfiles
from arsenalclient.interface.network_interfaces import NetworkInterfaces
from arsenalclient.interface.node_groups import NodeGroups
from arsenalclient.interface.nodes import Nodes
from arsenalclient.interface.physical_devices import PhysicalDevices
from arsenalclient.interface.physical_elevations import PhysicalElevations
from arsenalclient.interface.physical_locations import PhysicalLocations
from arsenalclient.interface.physical_racks import PhysicalRacks
from arsenalclient.interface.statuses import Statuses
from arsenalclient.interface.tags import Tags

# Log handling
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except (ImportError, AttributeError):
    pass

LOG = logging.getLogger(__name__)

logging.VERBOSE = 11
logging.addLevelName(logging.VERBOSE, 'VERBOSE')
def verbose(self, message, *args, **kws):
    '''Set custom logging level for more logging information than info but less
    than debug.'''

    if self.isEnabledFor(logging.VERBOSE):
        # pylint: disable=W0212
        self._log(logging.VERBOSE, message, args, **kws)
logging.Logger.verbose = verbose

# requests is chatty
logging.getLogger('requests').setLevel(logging.WARNING)
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass


class Client(object):
    '''The arsenal client library.

    Usage:

      >>> from arsenalclient.client import Client
      >>> client = Client('/path/to/my/arsenal.ini', '/path/to/my/secret/arsenal.ini')
      >>> search = {
      ...     'name': 'myserver',
      ...     'status': 'inservice',
      ...     'exact_get': True,
      ... }
      >>> results = client.nodes.search(search)
      >>> resp = client.tags.assign('tag1', 'value1', 'nodes', results)
      INFO    - Command successful.
      INFO    - Assigning tag: tag1=value1
      INFO    -   nodes: myserver1.mycompany.com
      INFO    - Command successful.
      INFO    - Command successful.
      INFO    - Assigning tag: tag1=value1
      INFO    -   nodes: myserver2.mycompany.com
      INFO    - Command successful.

    Args:

        conf       : A string representing the path to the conf file.
        secret_conf: An optional string representing the path to the
            secret_conf file. The secret_conf is only needed if you are calling arsenal
            from a script and need to pass a username and password.

        args       : An optional namespace object passed from a cli. Keys defined in
            args override any settings in the config file.
    '''

    def __init__(self,
                 conf_file,
                 secret_conf_file=None,
                 args=None
                ):

        self.conf_file = conf_file
        self.secret_conf_file = secret_conf_file
        self.args = args
        self.session = requests.session()
        self.init_log_lines = []

        self.settings = Namespace()
        self.settings.api_host = None
        self.settings.api_protocol = None
        self.settings.conf = None
        self.settings.cookie_file = None
        self.settings.log_file = None
        self.settings.log_level = None
        self.settings.user_login = None
        self.settings.user_password = None
        self.settings.verify_ssl = None

        self.load_all_configs()
        self.init_logging()
        self.login_overrides()

        kwargs = {
            'settings': self.settings,
        }

        self.data_centers = DataCenters(**kwargs)
        self.hardware_profiles = HardwareProfiles(**kwargs)
        self.network_interfaces = NetworkInterfaces(**kwargs)
        self.node_groups = NodeGroups(**kwargs)
        self.nodes = Nodes(**kwargs)
        self.physical_devices = PhysicalDevices(**kwargs)
        self.physical_elevations = PhysicalElevations(**kwargs)
        self.physical_locations = PhysicalLocations(**kwargs)
        self.physical_racks = PhysicalRacks(**kwargs)
        self.statuses = Statuses(**kwargs)
        self.tags = Tags(**kwargs)

    def load_all_configs(self):
        '''Read in all our configuration settings from the main .ini and from the
        secrets.ini, if specified. Also stores init_log_lines to be logged
        after logging is fully configured. Also sets any overrides from args,
        if they were provided.
        '''

        self.load_main_conf()
        self.load_secret_conf()

        # Override from args if present
        if self.args:
            for arg in vars(self.args):
                if getattr(self.args, arg):
                    self.init_log_lines.append('Assigning arg: '
                                               '{0}={1}'.format(arg,
                                                                getattr(self.args,
                                                                        arg)))
                    setattr(self.settings, arg, getattr(self.args, arg))

        # Have to do this becasue it can be a boolean or a string.
        if self.settings.verify_ssl == 'True':
            self.settings.verify_ssl = bool(self.settings.verify_ssl)

        if self.settings.verify_ssl == 'False':
            self.settings.verify_ssl = bool('')

    def load_main_conf(self):
        '''Load all settings from self.conf_file.'''

        conf_parse = ConfigParser.ConfigParser()
        conf_parse.read(self.conf_file)
        for section in conf_parse.sections():
            for key, val in conf_parse.items(section):
                if val:
                    self.init_log_lines.append('Assigning setting: {0}={1}'.format(key,
                                                                                   val))
                    setattr(self.settings, key, val)

    def load_secret_conf(self):
        '''Load all settings from self.secret_conf_file.'''

        if self.secret_conf_file:
            secret_conf_parse = ConfigParser.SafeConfigParser()
            secret_conf_parse.read(self.secret_conf_file)
            for key, val in secret_conf_parse.items('user'):
                if val:
                    if key == 'user_password':
                        self.init_log_lines.append('Assigning secret setting: '
                                                   '{0}=HIDDEN'.format(key))
                    else:
                        self.init_log_lines.append('Assigning secret setting: '
                                                   '{0}={1}'.format(key, val))
                    setattr(self.settings, key, val)

    def login_overrides(self):
        '''Sets user_login to read_only if no login is defined.'''

        if not getattr(self.settings, 'user_login', None):
            LOG.debug('No user_login defined, setting to: read_only')
            setattr(self.settings, 'user_login', 'read_only')

    def init_logging(self):
        '''Configure logging and log settings and any overrides, if present.'''

        if self.settings.log_level:
            self.settings.log_level = getattr(logging, self.settings.log_level)
        else:
            self.settings.log_level = logging.INFO

        if getattr(self.settings, 'verbose', None):
            self.settings.log_level = logging.VERBOSE
        elif getattr(self.settings, 'debug', None):
            self.settings.log_level = logging.DEBUG
        elif getattr(self.settings, 'quiet', None):
            self.settings.log_level = logging.ERROR

        # Set up logging to file
        if getattr(self.settings, 'write_log', None):

            logging.basicConfig(level=self.settings.log_level,
                                format='%(asctime)s %(levelname)-8s- %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=self.settings.log_file,
                                filemode='a')

        root = logging.getLogger()
        root.setLevel(self.settings.log_level)

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(self.settings.log_level)
        format_msg = '%(levelname)-8s- %(message)s'
        if getattr(self.settings, 'timestamps', None):
            format_msg = '%(asctime)s %(levelname)-8s- %(message)s'
        formatter = logging.Formatter(format_msg)
        console.setFormatter(formatter)
        root.addHandler(console)

        # log our overrides now that logging is configured.
        for line in self.init_log_lines:
            LOG.debug(line)

        if getattr(self.settings, 'write_log', None):
            LOG.info('Messages are being written to the log file: '
                     '{0}'.format(self.settings.log_file))

        LOG.debug('Using server: {0}'.format(self.settings.api_host))
