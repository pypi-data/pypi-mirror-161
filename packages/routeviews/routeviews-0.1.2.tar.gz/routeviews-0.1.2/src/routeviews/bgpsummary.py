from ipaddress import ip_address
import io
from typing import List
import socket

import logging
from enum import Enum
import pkgutil
import textfsm

from netmiko import ConnectHandler


def is_valid_asn(asn):
    """Determine if a BGP Peer is valid, per: RFC-6996 (private ASNs).

    :return: False if this is this peer has a 'private AS number' (64512 - 65534 inclusive).
    """
    return asn < 64512 or asn > 65534


class BGPStates(Enum):
    IDLE = 10
    CONNECT = 20
    ACTIVE = 30
    OPENSENT = 40
    OPENCONFIRM = 50
    ESTABLISHED = 60


class BGPPeer:
    def __init__(self, asn: str, ip_addr: str, state: BGPStates):
        self.asn = int(asn)
        self.ip_addr = ip_address(ip_addr)
        self.state = state

    @staticmethod
    def from_fsm(peer_summary):
        # Parse out the simple details of the neighbor: IP, ASN
        ip_addr = peer_summary['neighbor']
        asn = peer_summary['neighbor_as']
        # Parse out the state and prefix_recieved_count
        if peer_summary['state_pfxrcd'].isnumeric():
            state = BGPStates.ESTABLISHED
        elif peer_summary['state_pfxrcd'].lower() == 'connect':
            state = BGPStates.CONNECT
        elif peer_summary['state_pfxrcd'].lower().startswith('idle'):
            state = BGPStates.IDLE
        elif peer_summary['state_pfxrcd'].lower() == 'active':
            state = BGPStates.ACTIVE
        elif peer_summary['state_pfxrcd'].lower() == 'openconfirm':
            state = BGPStates.OPENCONFIRM
        elif peer_summary['state_pfxrcd'].lower() == 'opensent':
            state = BGPStates.OPENSENT
        else:
            raise ValueError("Unable to parse BGPPeer via textfsm; could not determine peer_state from provided "
                             f"'state_pfxrcd' data: {peer_summary['state_pfxrcd']}.")

        return BGPPeer(asn, ip_addr, state)

    def has_valid_asn(self):
        """Determine if a BGP Peer is valid, per: RFC-6996 (private ASNs).

        :return: False if this is this peer has a 'private AS number' (64512 - 65534 inclusive).
        """
        return is_valid_asn(self.asn)

    def __str__(self):
        return f"ASN: {self.asn} ADDR: {self.ip_addr} STATE: {self.state}"


class BGPSummary:
    def __init__(self, ip_addr: str, asn: str, peers: List[BGPPeer] = None):
        self.peers = peers if peers else []
        self.my_ip_addr = ip_address(ip_addr)
        self.my_asn = int(asn)

    def add_peer(self, peer: BGPPeer):
        self.peers.append(peer)

    def has_valid_asn(self):
        """Determine if a BGP Peer is valid, per: RFC-6996 (private ASNs).

        :return: False if this is this peer has a 'private AS number' (64512 - 65534 inclusive).
        """
        return is_valid_asn(self.my_asn)

    def __str__(self):
        return f"{[str(x) for x in self.peers]}"


def textfsm_parse_bgp_summary(raw_text):
    # Setup our TextFSM instance to parse raw_text
    template_raw = pkgutil.get_data('routeviews', 'templates/bgp_summary.tmpl')
    template_file = io.BytesIO(template_raw)
    fsm = textfsm.TextFSM(template_file)
    parsed_peers = fsm.ParseText(raw_text)

    # TODO Extract this code: This is entirely GENERIC code -- it will work for ALL textFSM templates/results
    # Do some post-TextFSM processing: to make the returned data more useful
    peers = []
    for peer in parsed_peers:
        peer_data = {}
        for i in range(len(fsm.header)):
            peer_data[fsm.header[i].lower()] = peer[i]
        peers.append(peer_data)
    return peers


def parse_bgp_summary(raw_text):
    parsed_data = textfsm_parse_bgp_summary(raw_text)

    # Validate that there is at least ONE peer
    if len(parsed_data) == 0:
        raise ValueError("For this script to succeed, the RouteViews collector must have at least one BGP peer.")

    summary = BGPSummary(
        ip_addr=parsed_data[0]['router_id'], 
        asn=parsed_data[0]['local_as']
    )
    for bgp_peer_summary in parsed_data:
        peer = BGPPeer.from_fsm(bgp_peer_summary)
        if not peer.has_valid_asn():
            raise ValueError("Encountered an invalid ASN when parsing BGP Peer data.")
        summary.add_peer(peer)
    return summary


def get_bgp_summary(collector):
    logging.info(f"Connecting to colllector (via netmiko): {collector}")
    try:
        connection = ConnectHandler(host=collector, device_type='cisco_ios_telnet', use_keys=True, timeout=15)
    except socket.gaierror:  # gaierror: Get Address Info error (aka DNS lookup error)
        raise NameError(f'DNS lookup failed for: {collector}')
    response = connection.send_command('show bgp summary')
    logging.info(f"Recived response from colllector (via netmiko): {collector}")

    # Parse output and return the result
    # TODO consider a try/catch here.
    return parse_bgp_summary(response)
