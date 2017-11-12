Project
=======

Project files setup:

settings.py
-----------

.. code-block:: python

    from xenops.data import converter

    CONNECTORS = {
        'pim_live': {
            'service': 'pim',  # Code of service
            'name': 'Live pim',  # optional verbose name
            'config': {  # Config for service like SOAP url and login
                'url': '',
                'username': '',
                'password': '',
            },
            'mapping': {  # Mapping per DataType code
                'product': {
                    'type': 'merge', # merge or replace, Default merge
                    'attributes': [
                        converter.Attribute('sku', 'ean'),
                    ]
                }
            },
            'triggers': [  # Triggers you want to run
                {
                    'trigger_code': 'update_product',  # optional, use type code as default
                    'type': 'product',  # DataType for which the trigger is run.
                    'cron': '1 * * * *',  # Cron for when to run the trigger (Not supported now).
                }
            ],
            'enhancers': [
                {
                    'type': 'product',
                    'attributes': ['price', 'qty'], # default will enhance type with all attributes from mapping
                }
            ],
            'processes': [
                {
                    'type': 'product',
                    'attributes': ['price', 'qty'], # only run this process when given attributes are changed (Not support now)
                },
            ]
        },
    }

    TYPES = {
        'product': {
            'mode': 'merge', # merge or replace, default merge
            'attributes': {
                'price': {
                    'allowed_value': r'\d+\.\d{2}'  # Regex for checking value.
                }
            }
        }
    }


Command line
------------

.. code-block:: python

    import sys
    import os

    os.environ.setdefault("XENOPS_SETTINGS", "settings")

    from xenops import execute_from_command_line

    execute_from_command_line(sys.argv)

