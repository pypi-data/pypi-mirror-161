"""Parse strings or bytes into Python objects.

See more info in docs/design.md
"""
import ipaddress
import logging
from typing import List

import routeviews.types

logger = logging.getLogger(__name__)


def IPAddr(ipaddr: str) -> routeviews.types.IPAddr:
    try:
        ipaddr_without_cidr = ipaddr.split('/')[0]
        return ipaddress.ip_address(ipaddr_without_cidr)
    except (ValueError, AttributeError):
        logger.debug(f'Invalid IP Address {ipaddr}')


def IPAddrList(ipaddrs_raw: List[str]) -> routeviews.types.IPAddrList:
    """Parse ip addresses.

    Args:
        ipaddrs_raw (List[str]): List of IP Address strings.

    Returns:
        routeviews.types.IPAddrList: The IP Addresses found in the provided data.
    """
    ipaddrs = [IPAddr(ip) for ip in ipaddrs_raw]
    return list(filter(None, ipaddrs))
