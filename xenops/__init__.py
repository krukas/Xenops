"""
xenops
~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from xenops.cli import Command


def execute_from_command_line(argv):
    """Run Xenops command line"""
    Command(argv)
