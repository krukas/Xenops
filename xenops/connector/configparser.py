"""
xenops.connector.configparser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging

from xenops.data.converter import BaseConverter
from xenops.service import ServiceFactory

logger = logging.getLogger(__name__)


class InvalidConnectorConfig(Exception):
    """Invalid Connector config Exception"""

    pass


class ConnectorConfig:
    """Connector config parser class"""

    def parse(self, config):
        """
        Parse given config and return dict with values for Connector __init__

        :param dict config:
        :return dict:
        """
        self.validate(config)
        service = ServiceFactory.get(config.get('service'))

        return {
            'code': config.get('code'),
            'service': service,
            'verbose_name': config.get('verbose_name'),
            'service_config': config.get('service_config'),
            'mapping': self.parse_mapping(service, config),
            'triggers': self.parse_triggers(service, config),
            'enhancers': config.get('enhancers'),
            'processes': config.get('processes')
        }

    def validate(self, config):
        """
        Validate base config

        :param str config:
        """
        if not config.get('code'):
            raise InvalidConnectorConfig('Config must have a code!')

        if not ServiceFactory.get(config.get('service')):
            raise InvalidConnectorConfig('Config is missing or has invalid service code')

        self.validate_mapping(config.get('mapping'))

    def validate_mapping(self, mapping):
        """
        Validate connector mapping

        :param dict mapping:
        :raises InvalidConnectorConfig:
        """
        valid = True

        if type(mapping) is not dict:
            raise InvalidConnectorConfig('Mapping config is not an dict')

        for type_code, config in mapping.items():
            pass

        return valid

    def parse_mapping(self, service, config):
        """
        Parse mapping

        :param xenops.service.Service service:
        :param dict config:
        :return dict:
        """
        mappings = {}

        # set default mappings
        for type_code, type_service in service.types.items():
            type_mapping = {}
            for converter in type_service.mapping:
                # @TODO Validate if attribute code exists in type
                if self.valid_converter_class(converter):
                    type_mapping[converter.attribute] = converter
                else:
                    logger.warning(
                        'Mapping value for ({}) on ({}) is not a valid converter class'.format(converter, type_code))
            mappings[type_code] = type_mapping

        # loop conn mapping
        for type_code, mapping in config.get('mapping', {}).items():
            service_type = service.types.get(type_code)

            if not service_type:
                logger.warning('could not create mapping for ({}), type does not exits for service'.format(type_code))
                continue

            type_mapping = mappings.get(type_code, {})
            if mapping.get('type', 'merge') != 'merge':
                type_mapping = {}

            for converter in mapping.get('attributes', []):
                # @TODO Validate if attribute code exists in type
                if self.valid_converter_class(converter):
                    type_mapping[converter.attribute] = converter
                else:
                    logger.warning(
                        'Mapping value for ({}) on ({}) is not a valid converter class'.format(converter, type_code))

        return mappings

    def valid_converter_class(self, value):
        """
        Validate if given object is an converter object

        :param str value:
        :return bool:
        """
        try:
            return isinstance(value, BaseConverter)
        except:  # noqa E722
            return False

    def parse_triggers(self, service, config):
        """
        Parse trigger config

        :param xenops.service.Service service:
        :param dict config:
        :return dict:
        """
        triggers = {}

        for trigger in config.get('triggers', []):
            if type(trigger) is dict:
                if service.types.get(trigger.get('type')):
                    triggers[trigger.get('type')] = trigger  # @TODO Add trigger config validation.
                else:
                    logger.warning(
                        "Could not create trigger for type ({}),"
                        " because trigger type does not exists for ({}) service".format(
                            trigger.get('type'),
                            service.code,
                        ))
            else:
                logger.error('Invalid trigger config supplied, only string or dictionary are valid!')

        return triggers
