"""
xenops.connector.connector
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
import datetime

from xenops.service import TriggerRequest, GetRequest, ProcessRequest
from xenops.data import DataMapObject, Enhancer

from .configparser import ConnectorConfig

logger = logging.getLogger(__name__)


class InvalidCode(Exception):
    """Invalid code Exception"""

    pass


class Connector:
    """Connector"""

    def __init__(self, app, code, service, verbose_name=None, service_config=None, mapping=None, triggers=None,
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

        # TODO: Lock trigger if trigger is already running
        trigger_request = TriggerRequest(
            service_config={},
            trigger_config={},
            last_run=datetime.datetime.now()  # TODO: get value from DB
        )
        for object_data in service_type.trigger(trigger_request):
            enhancers = []
            for enhancer_config in enhancer_configs:
                enhancers.append(Enhancer(
                    connector=enhancer_config['connector'],
                    mapping=enhancer_config['mapping'],
                    attributes=enhancer_config['attributes']
                ))

            data = DataMapObject(
                connector=self,
                datatype=service_type.datatype,
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
                            process_config={},
                            data_objects=[data]
                        ))
                    logger.info(' - Object id for ({}) is {}'.format(data, object_id))
                except Exception as e:
                    logger.error('Error processing data for process ({}:{}): {}'.format(
                        process_config['connector'].code,
                        service_type.datatype.code,
                        str(e)
                    ))

    def get(self, datatype, object_id, generic_id=None):
        """
        Get data from service for give type and id

        :param datatype:
        :param str generic_id:
        :param str object_id:
        :return:
        """
        service_type = self.service.types.get(datatype.code)
        if not service_type:
            raise Exception('There is no service type for given type code')

        # TODO: add id and generic_id to mapping type config
        object_data = service_type.get(GetRequest(service_config={}, object_id=object_id, generic_id=generic_id))

        enhancers = []
        for enhancer_config in self.get_enhancers_config(datatype.code):
            enhancers.append(Enhancer(
                connector=enhancer_config['connector'],
                mapping=enhancer_config['mapping'],
                attributes=enhancer_config['attributes']
            ))

        return DataMapObject(
            connector=self,
            datatype=service_type.datatype,
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

    def get_mapping(self, datatype):
        """
        Get mapping for datatype

        :param datatype:
        :return:
        """
        return self.mapping.get(datatype.code, {})
