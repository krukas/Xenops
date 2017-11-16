import os
import unittest
import logging
from datetime import datetime

from xenops.data import DataTypeFactory
from xenops.connector.storage import ConnectorStorage


class TestConverter(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.storage_path = os.path.join(os.path.dirname(__file__), 'tmp.sqlite')
        self.storage = ConnectorStorage(self.storage_path)

        DataTypeFactory.register('product', {
            'attributes': {
                'date': {
                    'type': 'datetime',
                }
            }
        })
        self.datatype = DataTypeFactory.get('product')
        self.trigger1_date = datetime(year=2015, month=3, day=12, hour=10, minute=10, second=10)
        self.trigger2_date = datetime(year=2016, month=6, day=12, hour=11, minute=11, second=11)

        # Add sample data
        self.storage.set_object_id(self.datatype, 'local_id-1', 'object_id-1')
        self.storage.set_object_id(self.datatype, 'local_id-2', 'object_id-2')
        self.storage.set_object_id(self.datatype, 'local_id-3', 'object_id-3')

        self.storage.set_last_run_time('test_trigger_1', self.trigger1_date)
        self.storage.set_last_run_time('test_trigger_2', self.trigger2_date)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        self.storage = None

        try:
            os.remove(self.storage_path)
        except Exception:
            pass

    def test_last_run_invalid(self):
        with self.assertRaises(AttributeError):
            self.storage.set_last_run_time('test_trigger', None)

    def test_get_last_run(self):
        self.assertEqual(self.storage.get_last_run('test_trigger_1'), self.trigger1_date)
        self.assertEqual(self.storage.get_last_run('test_trigger_2'), self.trigger2_date)

    def test_invalid_last_run(self):
        query = """REPLACE INTO triggers (trigger_code, last_run) VALUES (?, ?)"""

        self.storage.execute_query(query, ['invalid_trigger', 'random value'])

        self.assertEqual(self.storage.get_last_run('invalid_trigger'), None)

    def test_get_object_id(self):
        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-1'), 'object_id-1')
        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-2'), 'object_id-2')
        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-2'), 'object_id-2')

    def test_get_no_object_id(self):
        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-none'), None)

    def test_get_local_id(self):
        self.assertEqual(self.storage.get_local_id(self.datatype, 'object_id-1'), 'local_id-1')
        self.assertEqual(self.storage.get_local_id(self.datatype, 'object_id-2'), 'local_id-2')
        self.assertEqual(self.storage.get_local_id(self.datatype, 'object_id-3'), 'local_id-3')

    def test_get_no_local_id(self):
        self.assertEqual(self.storage.get_local_id(self.datatype, 'object_id-none'), None)

    def test_update_local_id(self):
        self.storage.update_local_id('local_id-1', 'local_id-1-new')

        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-1'), None)
        self.assertEqual(self.storage.get_object_id(self.datatype, 'local_id-1-new'), 'object_id-1')

    def test_execute_invalid_query(self):
        self.assertFalse(self.storage.execute_query("INVALID QUERY"))
