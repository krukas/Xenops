import unittest

from xenops.data.converter import Mapper


class TestConverterMapper(unittest.TestCase):

    def test_import_mapper(self):
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

        self.assertEqual(att.import_attribute(data), 'f')

    def test_import_mapper_default(self):
        data = {
            'gender': 10,
        }

        att = Mapper(
            attribute='gender',
            service_attribute='gender',
            mapping={
                'f': 2,
            },
            use_default=True,
            import_default='n'
        )

        self.assertEqual(att.import_attribute(data), 'n')

    def test_import_mapper_keyerror(self):
        data = {
            'gender': 10,
        }

        att = Mapper(
            attribute='gender',
            service_attribute='gender',
            mapping={
                'f': 2,
            }
        )

        with self.assertRaises(KeyError):
            att.import_attribute(data)
