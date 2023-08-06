import ipaddress
from typing import List, Union

IPAddr = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
IPAddrList = List[IPAddr]
