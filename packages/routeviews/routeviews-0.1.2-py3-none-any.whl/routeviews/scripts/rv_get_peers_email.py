#!/usr/bin/env python3
import logging

import configargparse 

from routeviews import bgpsummary
from routeviews.peers.contact_info import get_addresses


def main():
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    run(args)


def run(args):
    bgp_summary = bgpsummary.get_bgp_summary(args.collector)

    # Get the email address for each peer ASN
    emails = get_addresses.get_email_address_for_established_peers(bgp_summary.peers, args.peeringdb_auth)

    print('; '.join(emails) + ';')

    # Print  data
    # for peer in bgp_summary.peers:
    #     maint_start = None
    #     maint_end  = None
    #     if args.start_maintenance_time:
    #         maint_start = args.start_maintenance_time
    #     else:
    #         maint_start = ""
    #     if args.end_maintenance_time:
    #         maint_end = args.end_maintenance_time
    #     else:
    #         maint_end = ""
    #     try:
    #         print('--------------------------------------------------------------------------------------------------------------')
    #         print(f'email address: {emails[peer]}')
    #         print('--------------------------------------------------------------------------------------------------------------')
    #         print(f'Dear AS{peer.asn},')
    #         print('RouteViews will be performing maintenance on one of our collectors which you have a BGP peering session with.')
    #         if ip_address(peer.ip_addr).version == 4:
    #             print(f'RouteViews IP address: {collector_info["ipv4"]}')
    #         else:
    #             print(f'RouteViews IP address: {collector_info["ipv6"]}')
    #         print(f'Peer IP Address: {peer.ip_addr}')
    #         print('RouteViews AS: 6447')
    #         print(f'Peer AS: {peer.asn}')
    #         print(f'Location: {collector_info.get("location","")}')
    #         print(f'Maintenance start time: {maint_start}')
    #         print(f'Maintenance end time: {maint_end}')
    #         print("")
    #         print("Thanks,")
    #         print(" - RouteViews")
    #         print('--------------------------------------------------------------------------------------------------------------')
    #         print("")
    #         print("")
    #     except KeyError:
    #         print(f'# No email address found for: {peer.asn}')


def parse_args():
    parser = configargparse.ArgumentParser()
    parser.add_argument(
        '-c', '--collector', 
        required=True, 
        help='The Route Views collector of interest.'
    )
    # parser.add_argument(
    #     '-s', '--start-maintenance-time', 
    #     help="The UTC time that maintenance will start."
    # )
    # parser.add_argument(
    #     '-e', '--end-maintenance-time', 
    #     help="The UTC time that maintenance will end."
    # )
    # parser.add_argument(
    #     '-l', '--location', 
    #     help="The exchange the collector is at, or 'multi-hop'. See peeringdb for IX locations"
    # )
    parser.add_argument(
        '-u', '--peeringdb-username', 
        env_var='PEERINGDB_USERNAME', 
        help='Username for your PeeringDB account.'
    )
    parser.add_argument(
        '-p', '--peeringdb-password', 
        env_var='PEERINGDB_PASSWORD', 
        help='Password for your PeeringDB account.'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true'
    )

    args = parser.parse_args()
    # Process PeeringDB credentials into a custom "peeringdb_auth" tuple
    args.peeringdb_auth = None
    if args.peeringdb_username and args.peeringdb_password:
        args.peeringdb_auth = (args.peeringdb_username, args.peeringdb_password)
    return args


if '__main__' in __name__:
    main()
