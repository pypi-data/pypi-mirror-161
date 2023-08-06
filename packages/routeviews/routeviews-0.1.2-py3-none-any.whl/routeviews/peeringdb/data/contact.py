import dataclasses
from typing import Dict
from datetime import datetime

import routeviews.peeringdb.parse


@dataclasses.dataclass
class Contact:
    """_summary_

    Example raw data:
        | id      | 21478                |
        | role    | NOC                  |
        | visible | Public               |
        | name    | NOC                  |
        | phone   | 14 3316-7301         |
        | email   | noc@provedorway.com  |
        | url     |                      |
        | created | 2017-10-13T12:10:21Z |
        | updated | 2017-10-13T12:10:21Z |
        | status  | ok                   |
    """
    created: datetime
    email: str
    id: int
    name: str
    phone: str
    role: str
    status: str
    last_updated: datetime
    url: str
    visible: str

    def technical_prowess(self) -> int:
        """Try to determine this contact's technical prowess/capability.

        Note: Useful for sorting contact info by technical_prowess.

        network = 
        sort(key=PeeringDBContact.technical_prowess, network.points_of_contact)

        Returns:
            int: A number in [0,infinity). Lower implies more technically capable.
        """
        # Lower return value => 'more technically capable'
        if self.role == 'NOC':
            return 0
        elif self.role == 'Maintenance':
            return 100
        elif self.role == 'Technical':
            return 200
        elif self.role == 'Policy':
            return 300
        elif self.role == 'HR':
            return 900
        else:
            return 999999999

    @classmethod
    def from_data(cls, data: Dict):
        """Parse the Contact object from python native data structures.

        Args:
            neighbor_data (Dict): The data, e.g. parsed from a HTTP JSON response.

        Raises:
            KeyError: If the provided data structure does not contain expected key(s).

        Returns:
            Contact: The new contact object.
        """
        return cls(
            created=routeviews.peeringdb.parse.DateTime(data['created']),
            last_updated=routeviews.peeringdb.parse.DateTime(data['updated']),
            email=data['email'],
            id=data['id'],
            name=data['name'],
            phone=data['phone'],
            role=data['role'],
            status=data['status'],
            url=data['url'],
            visible=data['visible']
        )
