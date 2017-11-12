import unittest

from xenops.data import DataMapObject
from xenops.data.converter import Attribute, Mapper


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

    def test_attribute_no_data(self):
        att = Attribute(
            attribute='qty',
            service_attribute='stock.level'
        )
        with self.assertRaises(KeyError):
            att.import_attribute({})

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

    def test_attribute_representation(self):
        att = Attribute(
            attribute='stock',
            service_attribute='stock.level'
        )

        self.assertEquals(str(att), 'Attribute: {attribute: stock,  service_attribute: stock.level}')

    def test_convert_to_mapping(self):
        from_mapping = {
            'sku': Attribute(
                attribute='sku',
                service_attribute='sku'
            ),
            'qty': Attribute(
                attribute='qty',
                service_attribute='qty'
            )
        }

        data = DataMapObject(
            None,
            from_mapping,
            [],
            {
                'sku': 'ean-123',
                'qty': 10,
            }
        )

        to_data = data.export_to({
            'sku': Attribute(
                attribute='sku',
                service_attribute='ean'
            ),
            'qty': Attribute(
                attribute='qty',
                service_attribute='stock.level'
            )
        })

        self.assertDictEqual(to_data, {
            'ean': 'ean-123',
            'stock': {
                'level': 10
            }
        })

    def test_mapper(self):
        data = {
            'gender': 2,
        }

        att = Mapper(
            attribute='gender',
            service_attribute='gender',
            mapping={
                'f': 2,
            }
        )

        self.assertEquals(att.import_attribute(data), 'f')
