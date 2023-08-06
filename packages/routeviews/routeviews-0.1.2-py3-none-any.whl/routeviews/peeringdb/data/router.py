import dataclasses
import ipaddress
from typing import List

from routeviews import parse, peeringdb, types


@dataclasses.dataclass(frozen=True)
class Router:
    """Represent a PeeringDB "Peering Exchange Point".

    Exmaple raw data:
        | id          | 34335                |
        | ix_id       | 3                    |
        | name        | Equinix Dallas       |
        | ixlan_id    | 3                    |
        | notes       |                      |
        | speed       | 10000                |
        | asn         | 14832                |
        | ipaddr4     | 206.223.118.132      |
        | ipaddr6     |                      |
        | is_rs_peer  | False                |
        | operational | True                 |
        | created     | 2017-04-24T18:32:54Z |
        | updated     | 2017-04-24T18:32:54Z |
        | status      | ok                   |
    """
    id: int = None
    ix_id: int = None
    name: str = None
    ixlan_id: int = None
    notes: str = None
    speed: int = None
    asn: int = None
    ip4addr: ipaddress.IPv4Address = None
    ip6addr: ipaddress.IPv6Address = None
    is_rs_peer: bool = None
    operational: bool = None
    status: str = None

    @property
    def ipaddrs(self) -> types.IPAddrList:
        """Return all IP Addresses associated with this Router.

        Returns:
            types.IPAddrList: List of 0-2 IP Address associated to this router.
        """
        ipaddrs = []
        if self.ip4addr:
            ipaddrs.append(self.ip4addr) 
        if self.ip6addr:
            ipaddrs.append(self.ip6addr)
        return ipaddrs

    def can_ipv4_peer(self, other: 'Router') -> bool:
        if self.ip4addr and other.ip4addr:
            ipaddrs.append(other.ip4addr)  


    def peerable_ipaddrs(self, other: 'Router') -> List['types.IPAddr']:
        ipaddrs = []
        if self.ip4addr and other.ip4addr:
            ipaddrs.append(other.ip4addr)  
        if self.ip6addr and other.ip6addr:
            ipaddrs.append(other.ip6addr)
        return ipaddrs

    @classmethod
    def from_raw(cls, data):
        ip4addr = parse.IPAddr(data['ipaddr4'])
        ip6addr = parse.IPAddr(data['ipaddr6'])
        return cls(
            id=data['id'],
            ix_id=data['ix_id'],
            name=data['name'],
            ixlan_id=data['ixlan_id'],
            notes=data['notes'],
            speed=data['speed'],
            asn=data['asn'],
            ip4addr=ip4addr,
            ip6addr=ip6addr,
            is_rs_peer=data['is_rs_peer'],
            operational=data['operational'],
            status=data['status'],
        )
