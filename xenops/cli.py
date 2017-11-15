"""
xenops.cli
~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import sys
import argparse
import logging

from xenops.app import Application

logger = logging.getLogger()


class Command:
    """Xenops commandline"""

    def __init__(self, argv):
        """Init Setup Xenops"""
        parser = argparse.ArgumentParser(prog='xenops')
        parser.add_argument('--verbose', '-v', action='count', default=0)
        subparsers = parser.add_subparsers(help='sub-command help')

        trigger_parser = subparsers.add_parser('trigger', help='Run a trigger')
        trigger_parser.add_argument('connector', help='Code of connector')
        trigger_parser.add_argument('trigger', help='Code of trigger')
        trigger_parser.add_argument('-l', '--list', dest='list', action='store_true')
        trigger_parser.add_argument('--verbose', '-v', action='count', default=0)
        trigger_parser.set_defaults(func=self.trigger)

        args = parser.parse_args()

        if args.verbose:
            levels = [logging.WARNING, logging.INFO, logging.DEBUG]
            level = levels[min(len(levels) - 1, args.verbose)]
            logging.basicConfig(format="%(levelname)-8s: %(message)s", level=level)

        if not hasattr(args, 'func'):
            parser.print_help()
            exit()

        args.func(args)

    def trigger(self, args):
        """
        Run trigger sub command

        :param argparse.Namespace args:
        """
        app = Application()

        if args.list:
            print('Active triggers:\n')
            for connector in app.connectors.values():
                print('{} ({}):'.format(connector.code, connector.service.code))
                for trigger_code, config in connector.triggers.items():
                    print(' - {}'.format(trigger_code))
                    for key, value in config.items():
                        if key in ['type', 'trigger_code']:
                            continue
                        print('   - {}: {}'.format(key, value))
        else:
            app.trigger(args.trigger, args.connector)

    def validate_service(self, args):
        """Validate service (for service developers checking there config"""
        pass


if __name__ == '__main__':
    Command(sys.argv)
