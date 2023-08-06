"""Intelligently add peering information to Route Views Ansible inventory.
"""
import logging
import sys
from typing import List

import configargparse
import uologging
from routeviews import ansible, parse, peeringdb, types

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


def _main(args):
    if args.peeringdb_username and args.peeringdb_password or args.peeringdb_key:
        peeringdb.Repository(args.peeringdb_username, args.peeringdb_password, args.peeringdb_key)
    run(args.inventory, args.asn, args.ipaddrs, args.dry_run)


@trace
def run(inventory_path: str, asn: int, ipaddrs: List[types.IPAddr] = None, dry_run=True):
    inventory = ansible.load(inventory_path)
    possible_peer_requests = potential_peer_requests(asn)
    if ipaddrs:
        possible_peer_requests = list(filter(lambda peer_req: peer_req.your_address in ipaddrs, possible_peer_requests))
    inventory.peer_requests(possible_peer_requests)
    print(f'Changes:\n\n{inventory.diff()}')
    if dry_run:
        print("Note: Run again without '--dry-run' flag for these changes to apply.")
    else:
        inventory.save()


def potential_peer_requests(asn: int) -> List[peeringdb.PeerRequest]:
    routeviews_network = peeringdb.get_routeviews_info()
    requestor_network = peeringdb.get_network_info(asn)
    return routeviews_network.potential_peerings_with_network(requestor_network)


def parse_args(argv):
    parser = configargparse.ArgumentParser(
        description='Intelligently add peering information to Route Views Ansible inventory.')
    uologging.add_verbosity_flag(parser)
    parser.add_argument(
        '--inventory',
        required=True,
        env_var='ROUTEVIEWS_INVENTORY',
        help='''Provide the path to the "inventory/" directory 
        of your local copy of the Route Views ansible repo: 
        https://github.com/routeviews/infra (private)
        '''
    )
    parser.add_argument(
        '--asn', '-a',
        required=True,        
        help="The ASN to peer with."
    )
    parser.add_argument(
        '--ip', '-i',
        action='append',
        dest='ipaddrs',
        help="Specific IP address(es) to peer with. (If omitted, will attempt to peer with ALL compatible IP Addresses for ASN)"
    )
    # parser.add_argument(
    #     '-s', '--show-options',
    #     dest='show_options',
    #     action='store_true',
    #     help='Show potential peering options in a pretty table.'
    # )
    parser.add_argument(
        '-u', '--peeringdb-username', 
        env_var='PEERINGDB_USERNAME', 
        help='Username for your PeeringDB account. (If omitted, will use PeeringDB API anonymously)'
    )
    parser.add_argument(
        '-p', '--peeringdb-password', 
        env_var='PEERINGDB_PASSWORD', 
        help='Password for your PeeringDB account.'
    )
    parser.add_argument(
        '-k', '--peeringdb-key',
        env_var='PEERINGDB_KEY', 
        help='API Key for your PeeringDB account.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Do not make any changes to ansible inventory when running this script (for testing).",
    )
    args = parser.parse_args(argv[1:])
    # Do any argument pre-processing. E.g. convert strings to objects.
    if args.ipaddrs:
        args.ipaddrs = parse.IPAddrList(args.ipaddrs)
    return args


if __name__ == '__main__':
    logger.warning(f'Invoked as script, not using entry point {__file__}')
    run_main()


logger.debug(f'Loaded {__name__}')
