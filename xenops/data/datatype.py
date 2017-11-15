"""
xenops.data.datatype
~~~~~~~~~~~~~~~~~~~~

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
    def register(cls, code, config, mode=MODE_MERGE):
        # TODO: validate attributes
        """
        Register a date type.

        :param str code:
        :param list attributes:
        :param str mode:
        """
        logger.info("TODO: validate attributes")
        config.get('attributes'), config.get('generic_attribute_id')
        attributes = config.get('attributes', {})

        if code in cls._datatypes:
            datatype = cls._datatypes[code]
            datatype.generic_attribute_id = config.get('generic_attribute_id', datatype.generic_attribute_id)

            if mode == cls.MODE_MERGE:
                for attribute_code, attribute_config in attributes.items():
                    current_config = datatype.attributes.get(attribute_code, {})
                    for key, value in attribute_config.items():
                        current_config[key] = value
                    datatype.attributes[attribute_code] = current_config
            else:
                datatype.attributes = attributes
        else:
            datatype = DataType(code, attributes, config.get('generic_attribute_id', 'id'))

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

    def __init__(self, code, attributes, generic_attribute_id, verbose_name=''):
        """
        Init DataType

        :param str code:
        :param dict attributes:
        :param str generic_attribute_id:
        :param str verbose_name:
        """
        self.code = code
        self.attributes = attributes
        self.generic_attribute_id = generic_attribute_id
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
