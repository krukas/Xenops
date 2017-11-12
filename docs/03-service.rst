Service
=======

Dummy service files:

.. note::

    TODO: Make it possible to register service in project settings and rewrite existing services.

pim.py
------

.. code-block:: python

    from xenops.data import converter


    def trigger(request):
        # Based on request yield back data from source like (CSV, SOAP, REST, etc)
        yield {
            'ean': 'ean-123',
            'name': 'Test'
        }

        yield {
            'ean': 'ean-456',
            'name': 'Pim Product'
        }


    def get(request):
        # Based on request return data from source like (CSV, SOAP, REST, etc)
        return {
            'price': 14.5
        }


    def process(request):
        # process data and export to (CSV, SOAP, REST, etc) and return id
        return 827

    # Register service config (is used by setup.py entry_points)
    register = {
        'code': 'pim',
        'verbose_name': 'Pim',
        'type': {
            'product': {
                'mapping': [
                    converter.Attribute('sku', 'sku'),
                    converter.Attribute('price', 'price'),
                ],
                'trigger': trigger,
                'get': get,
                'process': process,
            }
        }
    }


.. code-block:: python

    from setuptools import setup, find_packages

    setup(
        name='xenops_service_pim',
        version="1.0",
        description="Xenops Pim service",
        author="Maikel Martens",
        packages=find_packages(),
        include_package_data=True,
        entry_points={
            'xenops.services': [
                'pim = pim:register'
            ]
        }
    )
