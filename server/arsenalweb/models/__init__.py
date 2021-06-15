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
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import configure_mappers
import zope.sqlalchemy

# Import or define all models here to ensure they are attached to the
# ``Base.metadata`` prior to any initialization routines.
from .common import User  # flake8: noqa
from .common import Group  # flake8: noqa
from .common import GroupPerm  # flake8: noqa
from .data_centers import DataCenter  # flake8: noqa
from .data_centers import DataCenterAudit  # flake8: noqa
from .ec2_instances import Ec2Instance  # flake8: noqa
from .ec2_instances import Ec2InstanceAudit  # flake8: noqa
from .hardware_profiles import HardwareProfile  # flake8: noqa
from .hardware_profiles import HardwareProfileAudit  # flake8: noqa
from .ip_addresses import IpAddress  # flake8: noqa
from .ip_addresses import IpAddressAudit  # flake8: noqa
from .network_interfaces import NetworkInterface  # flake8: noqa
from .network_interfaces import NetworkInterfaceAudit  # flake8: noqa
from .node_groups import NodeGroup  # flake8: noqa
from .node_groups import NodeGroupAudit  # flake8: noqa
from .nodes import Node  # flake8: noqa
from .nodes import NodeAudit  # flake8: noqa
from .operating_systems import OperatingSystem  # flake8: noqa
from .operating_systems import OperatingSystemAudit  # flake8: noqa
from .physical_devices import PhysicalDevice  # flake8: noqa
from .physical_devices import PhysicalDeviceAudit  # flake8: noqa
from .physical_elevations import PhysicalElevation  # flake8: noqa
from .physical_elevations import PhysicalElevationAudit  # flake8: noqa
from .physical_locations import PhysicalLocation  # flake8: noqa
from .physical_locations import PhysicalLocationAudit  # flake8: noqa
from .physical_racks import PhysicalRack  # flake8: noqa
from .physical_racks import PhysicalRackAudit  # flake8: noqa
from .statuses import Status  # flake8: noqa
from .statuses import StatusAudit  # flake8: noqa
from .tags import Tag  # flake8: noqa
from .tags import TagAudit  # flake8: noqa


# Run ``configure_mappers`` after defining all of the models to ensure
# all relationships can be setup.
configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager, request=None):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example:

      .. code-block:: python

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    This function may be invoked with a ``request`` kwarg, such as when invoked
    by the reified ``.dbsession`` Pyramid request attribute which is configured
    via the ``includeme`` function below. The default value, for backwards
    compatibility, is ``None``.

    The ``request`` kwarg is used to populate the ``sqlalchemy.orm.Session``'s
    "info" dict.  The "info" dict is the official namespace for developers to
    stash session-specific information.  For more information, please see the
    SQLAlchemy docs:
    https://docs.sqlalchemy.org/en/stable/orm/session_api.html#sqlalchemy.orm.session.Session.params.info

    By placing the active ``request`` in the "info" dict, developers will be
    able to access the active Pyramid request from an instance of an SQLAlchemy
    object in one of two ways:

    - Classic SQLAlchemy. This uses the ``Session``'s utility class method:

      .. code-block:: python

          from sqlalchemy.orm.session import Session as sa_Session

          dbsession = sa_Session.object_session(dbObject)
          request = dbsession.info["request"]

    - Modern SQLAlchemy. This uses the "Runtime Inspection API":

      .. code-block:: python

          from sqlalchemy import inspect as sa_inspect

          dbsession = sa_inspect(dbObject).session
          request = dbsession.info["request"]
    """
    dbsession = session_factory(info={"request": request})
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager
    )
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('sqla_demo.models')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # Use ``pyramid_tm`` to hook the transaction lifecycle to the request.
    # Note: the packages ``pyramid_tm`` and ``transaction`` work together to
    # automatically close the active database session after every request.
    # If your project migrates away from ``pyramid_tm``, you may need to use a
    # Pyramid callback function to close the database session after each
    # request.
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    # hook to share the dbengine fixture in testing
    dbengine = settings.get('dbengine')
    if not dbengine:
        dbengine = get_engine(settings)

    session_factory = get_session_factory(dbengine)
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    def dbsession(request):
        # hook to share the dbsession fixture in testing
        dbsession = request.environ.get('app.dbsession')
        if dbsession is None:
            # request.tm is the transaction manager used by pyramid_tm
            dbsession = get_tm_session(
                session_factory, request.tm, request=request
            )
        return dbsession

    config.add_request_method(dbsession, reify=True)
