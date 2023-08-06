"""TODO Single line discussing this script.

TODO Any supporting discussion (or delete). 
"""
import logging
import sys

import configargparse
import uologging

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
    # TODO Actually do work 
    print(args)


def parse_args(argv):
    parser = configargparse.ArgumentParser()
    uologging.add_verbosity_flag(parser)
    # TODO parser.add_argument(...)
    parser.add_argument(
        '--arg1',
        help='Just an example argument',
    )
    args = parser.parse_args(argv[1:])
    # TODO Do any argument pre-processing. E.g. convert strings to objects.
    return args


if __name__ == '__main__':
    logger.warning(f'Invoked as script, not using entry point {__file__}')
    run_main()


logger.debug(f'Loaded {__name__}')
