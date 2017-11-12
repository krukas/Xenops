import unittest

from xenops.data.converter import Attribute


class TestConverter(unittest.TestCase):

    def test_attribute(self):
        data = {
            'sku': 'ean-123',
        }

        att = Attribute(
            attribute='sku',
            service_attribute='sku'
        )

        self.assertEquals(att.import_attribute(data), 'ean-123')

    def test_attribute_nested(self):
        data = {
            'stock': {
                'level': 24
            }
        }

        att = Attribute(
            attribute='stock',
            service_attribute='stock.level'
        )

        self.assertEquals(att.import_attribute(data), 24)

    def test_attribute_keyerror(self):
        att = Attribute(
            attribute='sku',
            service_attribute='sku'
        )
        with self.assertRaises(KeyError):
            att.import_attribute({})