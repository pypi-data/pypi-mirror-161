"""Parse Ansible-related strings or bytes into Python objects.

Parse functions should only ever raise KeyErrors.
Other errors should be handled like so:
    * log at debug level, and 
    * return 'empty' by default. E.g. [], '', {}. (TODO: or return None?)
"""
import logging
from typing import Dict, List

import routeviews.ansible
import routeviews.parse
import routeviews.types

logger = logging.getLogger(__name__)


# TODO should this just take CollectorConfig as an argument instead?
# ... Are we starting to couple these data classes too closely?
def IPAddrList(interfaces_data: List[Dict[str,str]]) -> routeviews.types.IPAddrList:
    """Parse interfaces_data from a Route Views collector configuration.

    Args:
        interfaces_data (List[Dict[str,str]]): List of interface data.

    Example:
        >>> example_interfaces_data = [
        ...     {
        ...         'name': 'eth1',
        ...         'v4': '80.249.214.5/21',
        ...         'v6': '2001:7F8:1::A500:6447:1/64',
        ...     }
        ... ]
        >>> routeviews.ansible.parse.IPAddrList(example_interfaces_data)
        [IPv4Address('80.249.214.5'), IPv6Address('2001:7f8:1::a500:6447:1')]

    Returns:
        routeviews.types.IPAddrList: The IP Addresses found in the provided data.
    """
    ipaddrs = []
    for interface_data in interfaces_data:
        if 'v4' in interface_data:
            ipaddrs.append(routeviews.parse.IPAddr(interface_data['v4']))
        if 'v6' in interface_data:
            ipaddrs.append(routeviews.parse.IPAddr(interface_data['v6']))
    return ipaddrs
