"""
xenops.connector
~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
import datetime

from xenops.data.converter import BaseConverter
from xenops.service import ServiceFactory, TriggerRequest, GetRequest, ProcessRequest
from xenops.data import DataMapObject, Enhancer

logger = logging.getLogger(__name__)


class InvalidConnectorConfig(Exception):
    """Invalid Connector config Exception"""

    pass


class InvalidCode(Exception):
    """Invalid code Exception"""

    pass


class Connector:
    """Connector"""

    def __init__(self, app, code, service, verbose_name, service_config=None, mapping=None, triggers=None,
                 enhancers=None, processes=None):
        """
        Init Connector

        :param xenops.app.Application app:
        :param str code:
        :param xenops.service.Service service:
        :param str verbose_name:
        :param dict service_config:
        :param dict mapping:
        :param dict triggers:
        :param list enhancers:
        :param list processes:
        """
        self.app = app
        self.code = code
        self.service = service
        self.verbose_name = verbose_name if verbose_name else code
        self.service_config = service_config if service_config else {}
        self.mapping = mapping if mapping else {}
        self.triggers = triggers if triggers else {}
        self.enhancers = enhancers if enhancers else []
        self.processes = processes if processes else []

    @classmethod
    def create_connector(cls, app, config):
        """
        Create connector based on config

        :param xenops.app.Application app:
        :param dict config:
        :return Connector:
        """
        return cls(
            app,
            **ConnectorConfig().parse(config)
        )

    def execute_trigger(self, trigger_code):
        """
        Run trigger process based on trigger code

        :param str trigger_code:
        """
        trigger = self.triggers.get(trigger_code)
        if not trigger:
            raise InvalidCode('{} is not a valid trigger code for ({}) connector'.format(trigger_code, self.code))

        service_type = self.service.types.get(trigger_code)
        enhancer_configs = self.get_enhancers_config(service_type.datatype.code)
        process_configs = self.get_processes_config(service_type.datatype.code)

        # TODO: Save and load last trigger time, json file in project
        # TODO: Lock trigger if trigger is already running
        for object_data in service_type.trigger(TriggerRequest({}, datetime.datetime.now())):
            enhancers = []
            for enhancer_config in enhancer_configs:
                enhancers.append(Enhancer(
                    connector=enhancer_config['connector'],
                    mapping=enhancer_config['mapping'],
                    attributes=enhancer_config['attributes']
                ))

            data = DataMapObject(
                datatype=service_type.datatype,
                mapping=self.mapping.get(service_type.datatype.code, {}),
                enhancers=enhancers,
                data=object_data
            )

            # TODO: Make queue per processes and use multiple threads to call process function.
            # TODO: dont call process from own connector trigger

            for process_config in process_configs:
                logger.info('Processing {}:{} for object {}'.format(
                    process_config['connector'].code,
                    service_type.datatype.code,
                    data
                ))
                try:
                    object_id = process_config['connector'].service.types.get(service_type.datatype.code).process(
                        ProcessRequest(
                            connector=process_config['connector'],
                            config={},
                            data_object=data
                        ))
                    logger.info(' - Object id for ({}) is {}'.format(data, object_id))
                except Exception as e:
                    logger.error('Error processing data for process ({}:{}): {}'.format(
                        process_config['connector'].code,
                        service_type.datatype.code,
                        str(e)
                    ))

    def get(self, type_code, object_id):
        """
        Get data from service for give type and id

        :param str type_code:
        :param str object_id:
        :return:
        """
        service_type = self.service.types.get(type_code)
        if not service_type:
            raise Exception('There is no service type for given type code')

        # TODO: add id and generic_id to mapping type config
        object_data = service_type.get(GetRequest(object_id, generic_id='stub'))

        enhancers = []
        for enhancer_config in self.get_enhancers_config(type_code):
            enhancers.append(Enhancer(
                connector=enhancer_config['connector'],
                mapping=enhancer_config['mapping'],
                attributes=enhancer_config['attributes']
            ))

        return DataMapObject(
            datatype=service_type.datatype,
            mapping=self.mapping.get(service_type.datatype.code, {}),
            enhancers=[],  # todo add enhancers
            data=object_data
        )

    def get_enhancers_config(self, type_code):
        """
        Get list of enhancer configs

        :param str type_code:
        :return list:
        """
        # TODO: cache configs per type, maybe pre load on application
        configs = []
        for connector in self.app.connectors.values():
            mapping = connector.mapping.get(type_code, {})
            for enhancer_config in connector.enhancers:
                if enhancer_config.get('type') == type_code:
                    configs.append({
                        'connector': connector,
                        'mapping': mapping,
                        'attributes': enhancer_config.get('attributes', {})
                    })
        return configs

    def get_processes_config(self, type_code):
        """
        Get a list of process configs

        :param str type_code:
        :return list:
        """
        configs = []
        for connector in self.app.connectors.values():
            for process_config in connector.processes:
                if process_config.get('type') == type_code:
                    configs.append({
                        'connector': connector,
                        'attributes': process_config.get('attributes')
                    })
        return configs


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
