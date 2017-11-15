"""
xenops.data
~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging

logger = logging.getLogger(__name__)


class DataTypeFactory:
    """Datatype factory for registering and getting data types"""

    MODE_MERGE = 'merge'
    MODE_REPLACE = 'replace'

    _datatypes = {}

    @classmethod
    def register(cls, code, attributes, mode=MODE_MERGE):
        # TODO: validate attributes
        """
        Register a date type.

        :param str code:
        :param list attributes:
        :param str mode:
        """
        logger.info("TODO: validate attributes")

        if code in cls._datatypes:
            datatype = cls._datatypes[code]

            if mode == cls.MODE_MERGE:
                for attribute_code, attribute_config in attributes.items():
                    current_config = datatype.attributes.get(attribute_code, {})
                    for key, value in attribute_config.items():
                        current_config[key] = value
                    datatype.attributes[attribute_code] = current_config
            else:
                datatype.attributes = attributes
        else:
            datatype = DataType(code, attributes)

        cls._datatypes[code] = datatype

    @classmethod
    def get(cls, code):
        """
        Get DataType object based on data type code

        :param str code:
        :return xenops.data.DataType:
        """
        return cls._datatypes.get(code)


class DataType:
    """DataType class"""

    def __init__(self, code, attributes, verbose_name=''):
        """
        Init DataType

        :param str code:
        :param dict attributes:
        :param str verbose_name:
        """
        self.code = code
        self.attributes = attributes
        self.verbose_name = verbose_name if verbose_name else code.replace('_', '').title()

    def is_valid_attribute(self, code):
        """
        Check if given code is a valid attribute code for data type

        :param str code:
        :return bool:
        """
        return code in self.attributes

    def is_valid_attribute_value(self, code, value):
        """
        Validate if value is an valid value for given attribute code

        :param str code:
        :param value:
        :return bool:
        """
        # TODO: Add validation + spec out the attribute config
        return True


class DataMapObject:
    """DataMapObject for converting raw service data to datatype data"""

    def __init__(self, datatype, mapping, enhancers, data):
        """
        Init DataMapObject

        :param xenops.data.DataType datatype:
        :param dict mapping:
        :param list enhancers:
        :param dict data:
        """
        self.datatype = datatype
        self.mapping = mapping if mapping else {}
        self.enhancers = enhancers if enhancers else []
        self.data = data if data else {}
        self.cached_mapping_data = {}

        for enhancer in self.enhancers:
            enhancer.source_object = self

    def get_object_id(self, connector_code=None):
        """
        Get current connector object id or object id for given connector_code

        :param str connector_code:
        :return str:
        """
        # TODO: get current object id or id for connector_code
        # if connector_code and no id try to get id by servicetype.get call.

        # TODO: Check if object_id exists in DB and has same local_id, if not update local_id
        pass

    def get_generic_id(self):
        """
        Get generic object id from attribute datatype.generic_attribute_id

        :return str:
        """
        # TODO: Return generic attribute value set on datatype
        pass

    def get_local_id(self):
        """
        Get current local UUID or generate a new UUID

        :return str:
        """
        # TODO return random guid id used to map object_id's from different connecters together
        pass

    def get(self, key, default=None, raise_keyerror=False):
        """
        Get value from DataMapObject with datatype attribute code

        If there is an mapping for given key then will try to get value with that mapping.
        If there is no mapping or value it will check if one of the enhancers has the value.

        :param str key:
        :param default:
        :param bool raise_keyerror:
        :return:
        """
        if key in self.cached_mapping_data:
            return self.cached_mapping_data.get(key)

        if key in self.mapping:
            # @TODO Validate value is_valid_attribute_value
            try:
                value = self.mapping.get(key).import_attribute(self.data)
                self.cached_mapping_data[key] = value
                return value
            except KeyError:
                pass

        # try get value from enhancers
        for enhancer in self.enhancers:
            if enhancer.provide_attribute(key):
                value = enhancer.get(key, default, raise_keyerror)
                self.cached_mapping_data[key] = value
                return value

        if raise_keyerror:
            raise KeyError('Attribute ({}) does not exists'.format(key))

        return default

    def export_to(self, mapping, locale=None):
        """
        Convert datatype date to given mapping

        :param dict mapping:
        :param str locale:
        :return dict:
        """
        data = {}

        # TODO: get object by locale, add locale to GetRequest
        logger.debug('TODO: export_to locale')

        for code, converter in mapping.items():
            try:
                value = converter.export_attribute(self)
            except KeyError:
                continue

            keys = converter.service_attribute.split('.')
            self.set_date_value(data, keys, value)

        return data

    def set_date_value(self, data, keys, value):
        """
        Set nested data value

        :param dict data:
        :param list keys:
        :param value:
        """
        key = keys[0]
        keys = keys[1:]

        if not keys:
            data[key] = value
        else:
            if key not in data:
                data[key] = {}
            self.set_date_value(data[key], keys, value)


class Enhancer:
    """Enhancer class"""

    def __init__(self, connector, mapping, attributes):
        """
        Init Enhancer class

        :param xenops.connector.Connector connector:
        :param dict mapping:
        :param list attributes:
        """
        self.connector = connector
        self.mapping = mapping
        self.attributes = attributes
        self.source_object = None
        self.data = None
        self.cached_mapping_data = {}

    def provide_attribute(self, attribute_code):
        """
        Check if given attribute code is provided by enhancer

        :param str attribute_code:
        :return:
        """
        return attribute_code in self.attributes

    def get(self, attribute_code, default=None, raise_keyerror=False):
        """
        Get value for given attribute code

        :param str attribute_code:
        :param default:
        :param bool raise_keyerror:
        :return:
        """
        if not self.data:
            self._load_data()

        return self.data.get(attribute_code, default, raise_keyerror)

    def _load_data(self):
        """Load DataMapObject"""
        self.data = self.connector.get(self.source_object.datatype.code, self.source_object.get('id'))
