"""
xenops.data.datamap
~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
import uuid

logger = logging.getLogger(__name__)


class DataMapObject:
    """DataMapObject for converting raw service data to datatype data"""

    def __init__(self, connector, datatype, enhancers, data):
        """
        Init DataMapObject

        :param xenops.data.DataType datatype:
        :param dict mapping:
        :param list enhancers:
        :param dict data:
        """
        self.connector = connector
        self.datatype = datatype
        self.mapping = connector.get_mapping(datatype)
        self.enhancers = enhancers if enhancers else []
        self.data = data if data else {}
        self.cached_mapping_data = {}
        self.local_id = None
        self.object_ids = {}
        """Object_ids hold object id by connector code"""

        for enhancer in self.enhancers:
            pass

    def set_object_id(self, object_id):
        """
        Set object id

        :param str object_id:
        :return:
        """
        if not self.local_id:
            self.local_id = self.connector.storage.get_local_id(self.datatype, object_id)
            if not self.local_id:
                self.local_id = uuid.uuid4().hex

        self.object_ids[self.connector.code] = object_id

        self.connector.storage.set_object_id(self.datatype, self.local_id, object_id)

    def get_object_id(self, connector=None):
        """
        Get current connector object id or object id for given connector

        :param connector:
        :return str:
        """
        if not connector:
            connector = self.connector

        # check for cached object_id
        if connector.code in self.object_ids:
            return self.object_ids[connector.code]

        object_id = None
        local_id = None

        # Try to get object id from current data
        service_type = connector.service.types.get(self.datatype.code)
        if self.connector.code == connector.code and service_type and service_type.id_converter:
            try:
                object_id = service_type.id_converter.import_attribute(self.data)
                local_id = self.local_id
            except KeyError:
                pass
        elif self.local_id:
            object_id = connector.storage.get_object_id(self.datatype, self. local_id)
            local_id = self.local_id

        # Try to get object id by using generic_id
        if not object_id:
            logger.debug('Try getting object id by generic_id')
            try:
                data = connector.get(self.datatype, None, self.get_generic_id())
                object_id = service_type.id_converter.import_attribute(data.data)
            except Exception:
                pass

        if not object_id:
            return None

        self.object_ids[connector.code] = object_id

        if not local_id:
            local_id = connector.storage.get_local_id(self.datatype, object_id)
            if not local_id:
                local_id = uuid.uuid4().hex
        elif self.local_id != local_id:
            for conn in connector.app.connectors.values():
                conn.storage.update_local_id(old_id=local_id, new_id=self.local_id)

        self.local_id = local_id
        connector.storage.set_object_id(self.datatype, local_id, object_id)

        return object_id

    def datatype_code(self):
        """Datatype code"""
        return self.datatype.code

    def get_generic_id(self):
        """
        Get generic object id from attribute datatype.generic_attribute_id

        :return str:
        """
        try:
            return self.mapping[self.datatype.generic_attribute_id].import_attribute(self.data)
        except KeyError:
            return None

    def get_local_id(self):
        """
        Get current local UUID or generate a new UUID

        :return str:
        """
        if not self.local_id:
            self.get_object_id()

        return self.local_id

    def get_update_at(self):
        """
        Get update at of object

        :return:
        """
        service_type = self.connector.service.types.get(self.datatype.code)
        if service_type and service_type.update_converter:
            try:
                return service_type.update_converter.import_attribute(self.data)
            except KeyError:
                return None
        return None

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
