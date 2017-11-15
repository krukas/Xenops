import unittest
import logging

from xenops.service import ServiceFactory, TriggerRequest, GetRequest, ProcessRequest, ServiceType


class TestConverter(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_service_register_empty(self):
        response = ServiceFactory.register({})

        self.assertFalse(response)

    def test_service_register_forgot_type(self):
        response = ServiceFactory.register({
            'code': 'pim'
        })

        self.assertFalse(response)

    def test_service_register(self):
        response = ServiceFactory.register({
            'code': 'pim',
            'verbose_name': 'Pim',
            'type': {
                'product': {
                    'trigger': lambda x: x,
                    'get': lambda x: x,
                    'process': lambda x: x,
                }
            }
        })

        self.assertTrue(response)

    def test_service_register_empty_type(self):
        response = ServiceFactory.register({
            'code': 'pim',
            'verbose_name': 'Pim',
            'type': {
                'product': {
                }
            }
        })

        self.assertTrue(response)

    def test_service_register_no_valid_datatype(self):
        response = ServiceFactory.register({
            'code': 'pim',
            'verbose_name': 'Pim',
            'type': {
                'some_random_not_valid_datatype_code': {
                }
            }
        })

        self.assertTrue(response)

    def test_get_service_by_code(self):
        ServiceFactory.register({
            'code': 'pim',
            'verbose_name': 'Pim',
            'type': {
                'product': {
                    'trigger': lambda x: x,
                    'get': lambda x: x,
                    'process': lambda x: x,
                }
            }
        })

        service = ServiceFactory.get('pim')

        self.assertEqual(service.code, 'pim')

    def test_init_trigger_request(self):
        TriggerRequest({}, {}, None)

    def test_init_get_request(self):
        GetRequest({}, None, None)

    def test_init_process_request(self):
        ProcessRequest(None, {}, None)

    def test_service_type_trigger(self):
        service_type = ServiceType(
            datatype=None,
            id_converter=None,
            update_converter=None,
            mapping=None,
            trigger=lambda x: [{'sku': '123'}],
            get=None,
            process=None
        )

        data = list(service_type.trigger({}))

        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], {'sku': '123'})
