"""
xenops.data.types
~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from .product import product

default_types = {
    'product': {
        'generic_attribute_id': 'sku',
        'attributes': product,
    },
}
