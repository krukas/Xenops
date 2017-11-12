"""
xenops.data.converter
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""


class BaseConverter:
    """
    Base converter

    Service attribute can lookup and export nested data like:

    .. code-block:: python

        # Service raw data
        {
            'stock': {
                'level': 10
            }
        }

        # Mapping
        service_attribute = 'stock.level'

    """

    def __init__(self, attribute, service_attribute):
        """
        Init BaseConverter

        :param str attribute:
        :param str service_attribute:
        """
        self.attribute = attribute
        self.service_attribute = service_attribute

    def import_attribute(self, data):
        """
        Convert raw service data to DataType data

        :param dict data:
        :return:
        """
        keys = self.service_attribute.split('.')
        return self.get_import_value(keys, data)

    def get_import_value(self, keys, data):
        """
        Recursive function for getting data from service data dict

        :param str keys:
        :param dict data:
        :return:
        """
        key = keys[0]
        keys = keys[1:]

        # TODO: Check if key is array value like: items[] or items[1]

        if not keys:
            if key not in data:
                raise KeyError()
            return data.get(key)

        if key in data:
            return self.get_import_value(keys, data.get(key))

        raise KeyError()

    def export_attribute(self, data_object):
        """
        Convert DataType data to service data

        :param xenops.data.DataType data_object:
        :return:
        """
        return data_object.get(self.attribute)

    def __str__(self):
        """
        Representation of converter

        :return str:
        """
        return '{}: {{attribute: {},  service_attribute: {}}}'.format(
            self.__class__.__name__,
            self.attribute,
            self.service_attribute
        )


class Attribute(BaseConverter):
    """Default attribute converter"""

    pass


class Mapper(BaseConverter):
    """
    Mapper attribute converter can be used to convert values to same base value example for gender:

    .. code-block:: python

        # Mapping for some erp service
        {
            'm': 1,
            'f': 2,
        }

        # Mapping for some e-commerce service
        {
            'm': 'Male',
            'f': 'Female',
        }
    """

    def __init__(self, attribute, service_attribute, mapping, use_default=False, import_default=None,
                 export_default=None):
        """
        Init Mapper

        :param attribute:
        :param service_attribute:
        :param mapping:
        :param default:
        """
        super().__init__(attribute, service_attribute)
        self.export_mapping = mapping
        self.import_mapping = {value: key for key, value in mapping.items()}
        self.use_default = use_default
        self.import_default = import_default
        self.export_default = export_default

    def import_attribute(self, data):
        """
        Get data from super and map value with mapping

        :param dict data:
        :return:
        """
        value = super().import_attribute(data)

        if value in self.import_mapping:
            return self.import_mapping[value]

        if self.use_default:
            return self.import_default

        raise KeyError()

    def export_attribute(self, data_object):
        """
        Get data from super and map value with mapping

        :param data_object:
        :return:
        """
        value = super().export_attribute(data_object)

        if value in self.export_mapping:
            return self.export_mapping[value]

        if self.use_default:
            return self.export_default

        raise KeyError()
