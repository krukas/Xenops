import unittest
from datetime import datetime

from xenops.data import DataMapObject
from xenops.data.converter import DateTime
from xenops.connector import Connector
from xenops.data import DataTypeFactory


class TestConverterMapper(unittest.TestCase):

    def setUp(self):
        DataTypeFactory.register('product', {
            'attributes': {
                'date': {
                    'type': 'datetime',
                }
            }
        })

        self.connector = Connector(
            app=None,
            storage=None,
            code='test',
            service=None,
            verbose_name=None,
            mapping={
                'product': {
                    'date': DateTime('date', 'date')
                }
            },
        )

    def test_import_format(self):
        converter = DateTime('date', 'date', '%Y-%m-%d %H:%M:%S')
        value = converter.import_attribute({'date': '2015-03-12 10:10:10'})
        valid_value = datetime(year=2015, month=3, day=12, hour=10, minute=10, second=10)

        self.assertEqual(valid_value, value)

    def test_import_empty(self):
        converter = DateTime('date', 'date', '%Y-%m-%d %H:%M:%S')
        self.assertEqual(converter.import_attribute({'date': ''}), None)

    def test_invalid_format(self):
        converter = DateTime('date', 'date', '%Y-%m-%d %H:%M:%S')
        value = converter.import_attribute({'date': '12-03-2015 10:10:10'})

        self.assertEqual(value, None)

    def test_export_format(self):
        data = DataMapObject(
            self.connector,
            DataTypeFactory.get('product'),
            [],
            {
                'date': '2015-03-12 10:10:10',
            }
        )

        to_data = data.export_to({
            'update_at': DateTime('date', 'update_at', '%d-%m-%Y')
        })

        self.assertDictEqual(to_data, {
            'update_at': '12-03-2015',
        })

    def test_export_none(self):
        data = DataMapObject(
            self.connector,
            DataTypeFactory.get('product'),
            [],
            {
                'date': '',
            }
        )

        to_data = data.export_to({
            'update_at': DateTime('date', 'update_at', '%d-%m-%Y')
        })

        self.assertDictEqual(to_data, {
            'update_at': None,
        })
