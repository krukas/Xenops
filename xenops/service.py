"""
xenops.service
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging

from xenops.data import DataTypeFactory

logger = logging.getLogger(__name__)


class TriggerRequest:
    """Trigger request"""

    def __init__(self, service_config, trigger_config, last_run):
        """
        Init trigger request

        :param dict service_config:
        :param dict trigger_config:
        :param datetime.datetime last_run:
        """
        self.service_config = service_config
        self.trigger_config = trigger_config
        self.last_run = last_run


class GetRequest:
    """Get request"""

    def __init__(self, service_config, object_id, generic_id):
        """
        Init get request

        :param dict service_config:
        :param str object_id:
        :param str generic_id:
        """
        self.service_config = service_config
        self.object_id = object_id
        self.generic_id = generic_id


class ProcessRequest:
    """Process request"""

    def __init__(self, connector, process_config, data_objects):
        """
        Init process request

        :param xenops.connector.Connector connector:
        :param dict process_config:
        :param xenops.data.DataMapObject[] data_objects:
        """
        self.connector = connector
        self.process_config = process_config
        self.data_objects = data_objects

    @property
    def service_config(self):
        """Service config"""
        return self.connector.service_config

    def get_object_id(self, data_object):
        """
        Get object id for current connector

        :param data_object:
        :return str:
        """
        return data_object.get_object_id(self.connector)

    def get_export_data(self, data_object):
        """
        Get exported data for current connector mapping

        :param data_object:
        :return dict:
        """
        return data_object.export_to(self.connector.get_mapping(data_object.datatype))


class Service:
    """Service class"""

    def __init__(self, code, verbose_name, service_types):
        """
        Init Service

        :param str code:
        :param str verbose_name:
        :param dict service_types:
        """
        self.code = code
        self.verbose_name = verbose_name
        self.types = service_types

    # TODO: Maybe add trigger/get/process(type_code, request)


class ServiceType:
    """Service type"""

    def __init__(self, datatype, id_converter, update_converter, mapping, trigger, get, process):
        """
        Init Service type

        :param xenops.data.DataType datatype:
        :param dict mapping:
        :param Callable trigger:
        :param Callable get:
        :param Callable process:
        """
        self.datatype = datatype
        self.id_converter = id_converter
        self.update_converter = update_converter
        self.mapping = mapping  # TODO: Move mapping to config, mapping is not used here
        self.trigger_function = trigger
        self.get_function = get
        self.process_function = process

    def trigger(self, request):
        """
        Run trigger

        :param xenops.service.TriggerRequest request:
        :return Generator[dict]:
        """
        for data in self.trigger_function(request):
            yield data

    def get(self, request):
        """
        Get data from service

        :param xenops.service.GetRequest request:
        :return dict:
        """
        return self.get_function(request)

    def process(self, request):
        """
        Process data from trigger

        :param xenops.service.ProcessRequest request:
        :return int: data object id from service
        """
        return self.process_function(request)


class ServiceFactory:
    """Service factory for registering and getting services"""

    _services = {}

    @classmethod
    def register(cls, config):
        """
        Register a service

        :param dict config:
        :return bool:
        """
        if not config.get('code'):
            logger.error('Service config must have a code!')
            return False

        if not config.get('type'):
            logger.error('Service must have at least one type!')

        types = {}
        for type_code, type_config in config.get('type').items():
            datatype = DataTypeFactory.get(type_code)

            if not datatype:
                logger.error('Service ({}) want to register data type ({}) that does not exists!'.format(config['code'],
                                                                                                         type_code))
                continue

            def trigger_function(*args, **kwargs):
                pass

            def get_function(*args, **kwargs):
                pass

            def process_function(*args, **kwargs):
                pass

            # TODO: Rename to objects
            if 'trigger' in type_config and callable(type_config['trigger']):
                trigger_function = type_config['trigger']  # noqa F811

            # TODO: Rename to object
            if 'get' in type_config and callable(type_config['get']):
                get_function = type_config['get']  # noqa F811

            if 'process' in type_config and callable(type_config['process']):
                process_function = type_config['process']  # noqa F811

            types[datatype.code] = ServiceType(
                datatype=datatype,
                id_converter=type_config.get('id'),
                update_converter=type_config.get('update_at'),
                mapping=type_config.get('mapping', {}),  # @TODO validate mapping
                trigger=trigger_function,
                get=get_function,
                process=process_function
            )

        cls._services[config['code']] = Service(
            code=config['code'],
            verbose_name=config.get('verbose_name'),
            service_types=types
        )

        return True

    @classmethod
    def get(cls, code):
        """
        Get a service based on a code

        :param str code:
        :return xenops.service.Service:
        """
        return cls._services.get(code)
