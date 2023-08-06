"""Auto-format Route Views' Ansible inventory.

Use after you make any manual changes to the Route Views Ansible inventory.

ℹ This tool effectively does a simple 'touch' of the Ansible inventory.
(formatting performed via the `routeviews.yaml` module)
"""
import logging
import sys

import configargparse
import uologging
from routeviews import ansible

logger = logging.getLogger(__name__)
trace = uologging.trace(logger, capture_args=False)


def run_main():
    main(sys.argv)


def main(argv):
    """Parse args, set up logging, then call the inner 'main' function. 
    """
    package_name = __name__.split('.')[0]
    uologging.init_console(package_name)
    args = parse_args(argv)
    uologging.set_logging_verbosity(args.verbosity_flag, package_name)
    _main(args)


@trace
def _main(args):
    if args.files:
        configs = list(map(ansible.CollectorConfig.load, args.files))
        [config.save() for config in configs]
    elif args.inventory:
        inventory = ansible.Inventory.load(args.inventory)
        inventory.save()
    else:
        print('No inventory or files provided. Use --help to learn more.')
        sys.exit(1)


def parse_args(argv):
    parser = configargparse.ArgumentParser(description=__doc__)
    uologging.add_verbosity_flag(parser)
    parser.add_argument(
        '--inventory',
        env_var='ROUTEVIEWS_INVENTORY',
        help='''Provide the path to the "inventory/" directory 
        of your local copy of the Route Views ansible repo: 
        https://github.com/routeviews/infra (private)
        '''
    )   
    parser.add_argument(
        '--file', '-f',
        action='append',
        dest='files',
        help="Specific file(s) to auto-format. If unspecified, the entire inventory will be auto-formatted."
    )
    args = parser.parse_args(argv[1:])
    # Do any argument pre-processing. E.g. convert strings to objects.
    return args


if __name__ == '__main__':
    logger.warning(f'Invoked as script, not using entry point {__file__}')
    run_main()


logger.debug(f'Loaded {__name__}')
