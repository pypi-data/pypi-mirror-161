import dataclasses
import ipaddress
import logging
from typing import Any, Dict, List

import routeviews.ansible
import routeviews.ansible.parse
import routeviews.const
import routeviews.defaults
import routeviews.parse
import routeviews.types
import routeviews.yaml

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CollectorConfig:
    filepath: str
    _raw_config: Dict
    neighbors: List['routeviews.ansible.NeighborConfig'] = routeviews.defaults.empty_list()
    new_neighbors: List['routeviews.ansible.NeighborConfig'] = routeviews.defaults.empty_list()

    @classmethod
    def load(cls, config_path: str):
        """Parse a CollectorConfig object from a YAML file.

        Args:
            filepath (str): The filepath for this config file.

        Returns:
            CollectorConfig.
        """        
        logger.debug(f"Loading: {config_path}")
        config_data = routeviews.yaml.load(config_path)
        return cls.from_data(config_path, config_data)

    @classmethod
    def from_data(cls, filepath: str, data: Dict):
        """Construct a CollectorConfig.

        Args:
            filepath (str): The filepath where this CollectorConfig will be saved as a file.
            data (Dict): The data that will populate this CollectorConfig.

        Returns:
            CollectorConfig.
        """
        neighbors = []
        if 'neighbors' in data and data['neighbors']:
            try: 
                neighbors = [
                    routeviews.ansible.NeighborConfig.from_data(neighbor_data)
                    for neighbor_data in data['neighbors']
                ]
            except TypeError:
                logger.warning(f'Unable to parse collector neighbors: {data["neighbors"]}')
        return cls(
            filepath=filepath,
            _raw_config=data,
            neighbors=neighbors,
        )

    @property
    def raw_config(self) -> Dict:
        """Get the config back out as python data, e.g. to be dumped via PYyaml. 

        Returns:
            Any: The data of this object, including all changes.
        """
        # Lazily 'sync' the raw_config on read access, e.g. for added neighbors.
        if self.new_neighbors:
            self._raw_config['neighbors'] = [
                neighbor.to_data()
                for neighbor in self.neighbors
            ]
        return self._raw_config

    @property
    def peerable_ipaddrs(self) -> routeviews.types.IPAddrList:
        try:
            return routeviews.ansible.parse.IPAddrList(self._raw_config['interface_config']['peering']['interfaces'])
        except KeyError:
            logger.info(f'No Peering Interfaces found in {self.filepath} (interface_config.peering.interfaces)')
            return []

    @property
    def neighbors_ipaddrs(self) -> routeviews.types.IPAddrList:
        return [neighbor.peer_address for neighbor in self.neighbors]

    def diff(self) -> str:
        if not self.new_neighbors:
            return ''
        messages = []
        for neighbor in self.new_neighbors:
            messages.append(neighbor.diff())
        messages_joined = "\n".join(messages)
        return f'Diff of "{self.filepath}"\n{messages_joined}'

    def is_peered_with(self, peer_ipaddr: routeviews.types.IPAddr):
        return any(
            existing_peer_ipaddr == peer_ipaddr
            for existing_peer_ipaddr in self.neighbors_ipaddrs
        )

    def add_neighbor(self, asn: int, address: routeviews.types.IPAddr, description: str, options: Dict = None) -> 'routeviews.ansible.NeighborConfig':
        """Establish a new peering with the provided asn (network) at the provided address (router).

        Args:
            asn (int): The Autonomous System Number of the network being peered with.
            address (routeviews.types.IPAddr): The IP Address of the router to peer with.
            description (str): The description to provide for this peering. (E.g. organization name is a good default)
            options (Dict, optional): Add BGP options to this peering configuration. Defaults to None.

        Returns:
            NeighborConfig: The configuration required to fulfill this peering.
        """
        if asn is None or address is None or description is None:
            raise TypeError('Must provide asn, address, and description arguments.')
        neighbor = routeviews.ansible.NeighborConfig(
            peer_as=asn,
            peer_address=address,
            description=description,
            options=options,
            afi_safis=infer_afi_safis(address),
        )
        self.neighbors.append(neighbor)
        self.new_neighbors.append(neighbor)
        return neighbor

    def save(self):
        self.save_as(self.filepath)

    def save_as(self, config_path):
        logger.info(f"Saving: {config_path}")
        with open(config_path, 'w') as out_file:
            out_file.write(self.as_yaml())

    def as_yaml(self) -> str:
        """Regenerate this configuration as YAML.

        Returns:
            str: The YAML representation of this object.
        """
        return routeviews.yaml.dump(self.to_data())

    def to_data(self) -> Any:
        return self.raw_config


def infer_afi_safis(ipaddr: routeviews.types.IPAddr) -> List[str]:
    """Given an IP Address, infer the appropriate 'afi_safi' string(s).

    Args:
        ipaddr (routeviews.types.IPAddr): The IP Address.

    Returns:
        List[str]: All possible matching AFI/SAFIs.
    """
    if ipaddr is None:
        return None

    possible_afi_safis = {
        ipaddress.IPv4Address: [routeviews.const.IPV4_UNICAST_AFI_SAFI],
        ipaddress.IPv6Address: [routeviews.const.IPV6_UNICAST_AFI_SAFI],
    }
    try:
        return possible_afi_safis[type(ipaddr)]
    except KeyError:
        raise ValueError(f'Expected a valid IPv4/6 address. Got {ipaddr}')
