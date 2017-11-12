"""
xenops.cli
~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import sys
import logging

from xenops.app import Application

logger = logging.getLogger()


class Command:
    """Xenops commandline"""

    def __init__(self, argv):
        """Init Setup Xenops"""
        logging.basicConfig(format="%(levelname)-8s: %(message)s", level=logging.DEBUG)

        # TODO add argparse

        # add option show flows: will show trigger -> enhances -> processes

        # Start app
        app = Application()
        app.trigger('product', 'pim_live')


if __name__ == '__main__':
    Command(sys.argv)
