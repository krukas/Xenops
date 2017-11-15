import unittest

from xenops.data import DataMapObject
from xenops.data.converter import Attribute
from xenops.connector import Connector
from xenops.data import DataTypeFactory


class TestConverter(unittest.TestCase):

    def setUp(self):
        DataTypeFactory.register('product', {
            'attributes': {
                'date': {
                    'sku': 'str',
                    'qty': 'str',
                }
            }
        })

        self.connector = Connector(
            app=None,
            code='test',
            service=None,
            verbose_name=None,
            mapping={
                'product': {
                    'sku': Attribute(
                        attribute='sku',
                        service_attribute='sku'
                    ),
                    'qty': Attribute(
                        attribute='qty',
                        service_attribute='qty'
                    )
                }
            },
        )

    def test_attribute(self):
        data = {
            'sku': 'ean-123',
        }

        att = Attribute(
            attribute='sku',
            service_attribute='sku'
        )

        self.assertEqual(att.import_attribute(data), 'ean-123')

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

        self.assertEqual(att.import_attribute(data), 24)

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

        self.assertEqual(str(att), 'Attribute: {attribute: stock,  service_attribute: stock.level}')

    def test_convert_to_mapping(self):
        data = DataMapObject(
            self.connector,
            DataTypeFactory.get('product'),
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
