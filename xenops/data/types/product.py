"""
xenops.data.types.product
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
product = {
    'sku': {
        'type': str,
        'verbose_name': 'Sku',
        'allowed_value': r'[\w\d]+',
    },
    'price': {
        'type': float,
    }
}
