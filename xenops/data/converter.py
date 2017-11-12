"""
xenops.data.converter
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""


class BaseConverter:
    """Base converter"""

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
