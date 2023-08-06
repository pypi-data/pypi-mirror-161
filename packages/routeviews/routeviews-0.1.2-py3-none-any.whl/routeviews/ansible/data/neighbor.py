import dataclasses
import logging
from typing import Dict, List

from routeviews import parse, types, yaml

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class NeighborConfig:
    peer_as: int
    peer_address: types.IPAddr
    description: str
    afi_safis: List[str]
    options: Dict = None

    @classmethod
    def from_data(cls, data: Dict):
        """Parse a NeighborConfig object from python native data structures.

        Args:
            neighbor_data (Dict): The data, e.g. parsed via PYyaml.

        Raises:
            KeyError: If the provided data structure does not contain expected key(s).

        Returns:
            NeighborConfig: A new neighbor config.
        """
        ipaddr = parse.IPAddr(data['peer_address'])
        return cls(
            peer_as=data['peer_as'],
            peer_address=ipaddr,
            description=data['description'],
            afi_safis=data['afi_safis'],
            options=data.get('options', None),
        )

    def to_data(self):
        data = {
            'peer_as': self.peer_as,
            'peer_address': str(self.peer_address),
            'description': self.description,
            'afi_safis': self.afi_safis,
        }
        if self.options:
            data['options'] = self.options
        return data

    def diff(self, diff_marker='+'):
        as_yaml = yaml.dump(self.to_data())
        diff_lines = []
        for line in as_yaml.split('\n'):
            if line:
                new_line = f'{diff_marker} {line}'
                diff_lines.append(new_line)
        return '\n'.join(diff_lines)
