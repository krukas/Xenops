"""
xenops.app
~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
from pkg_resources import iter_entry_points

from xenops.conf import settings
from xenops.service import ServiceFactory
from xenops.data import DataTypeFactory
from xenops.data.types import default_types
from xenops.connector import Connector, InvalidConnectorConfig

logger = logging.getLogger(__name__)


class Application:
    """Application holds all project data"""

    def __init__(self):
        """Load all services and project settings"""
        self.connectors = {}

        # Load all default product types
        for code, attributes in default_types.items():
            DataTypeFactory.register(code, attributes)

        self.load_services()

        if settings.IS_PROJECT:
            logger.debug("Loading project settings")
            self.load_project_types()
            self.load_project_connectors()

    def load_services(self):
        """Load all services registered with pkg_resources"""
        for entry_point in iter_entry_points(group='xenops.services', name=None):
            try:
                config = entry_point.load()
            except ImportError:
                logger.error('Could not load service: ({}), check your setup.py entry_points.'.format(entry_point))
                continue

            if type(config) != dict:
                logger.error('Service config ({}) is not an dict and will not be registered!'.format(entry_point))

            logger.debug("Registering ({}) service".format(entry_point))
            if not ServiceFactory.register(config):
                logger.error('Service ({}) could not be registered!'.format(entry_point))

    def load_project_types(self):
        """Load project types"""
        for code, config in settings.get('TYPES', {}).items():
            # TODO add validation
            DataTypeFactory.register(code, config['attributes'], config.get('type', 'merge'))

    def load_project_connectors(self):
        """Load project connectors"""
        for code, config in settings.get('CONNECTORS', {}).items():
            config['code'] = code
            try:
                self.connectors[code] = Connector.create_connector(self, config)
            except InvalidConnectorConfig as e:
                logger.error('Invalid connector ({}) config: {}'.format(code, e))

    def trigger(self, type_code=None, connector_code=None):
        """
        Trigger a connector data type import

        :param str type_code:
        :param str connector_code:
        """
        if not DataTypeFactory.get(type_code):
            raise Exception('Invalid type')

        if connector_code not in self.connectors:
            raise Exception('Connector does not exists')

        connector = self.connectors.get(connector_code)
        connector.execute_trigger(type_code)
