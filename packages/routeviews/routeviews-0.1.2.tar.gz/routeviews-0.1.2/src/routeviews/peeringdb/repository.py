import logging
from typing import Union

import requests
import routeviews.peeringdb
import routeviews.peeringdb.auth
from routeviews.peeringdb.auth import API_KEY_USERNAME

PEERINGDB_API_URL = 'https://www.peeringdb.com/api'


logger = logging.getLogger(__name__)

class Repository:
    instances = []

    def __init__(self, username: str = None, password: str = None, api_key: str = None):
        self._api_url = PEERINGDB_API_URL
        self._http_session = requests.session()
        self._peeringdb_organizations_cache = {}

        try: 
            auth_header = routeviews.peeringdb.auth.HTTP_header(username, password, api_key)
            self._http_session.headers['Authorization'] = auth_header
        except ValueError as e:
            logger.info(f'No PeeringDB credentials -- will use anonymous access. ({str(e)})')
        self.username = API_KEY_USERNAME if api_key else username

        Repository.instances.append(self)

    @property
    def http_session(self):
        return self._http_session

    def get(self, path: str, *args, **kwargs):
        """A simple wrapper around requests.get function.

        Args:
            path (str): The path to be appended to the PeeringDB API URL. E.g. '/net'.
                Leading '/' is expected.

        Raises:
            HTTPError: if one occurred.

        Returns:
            dict: The response's data.
        """
        url = f'{self._api_url}{path}'
        response = self.http_session.get(url, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_network_info(self, asn: Union[str,int]) -> 'routeviews.peeringdb.Network':
        """Get a network's information from PeeringDB, looked up by ASN.

        Args:
            asn (str,int): The ASN to lookup.

        Raises:
            ValueError: If the ASN is not found in PeeringDB.

        Returns:
            routeviews.peeringdb.Network: The network object.
        """
        params = {
            'asn': asn,
            'depth': 2,  # "expand sets into objects (slower)," and provides ALL the data we need!
        }
        response = self.get('/net', params=params)
        try:
            assert len(response['data']) == 1, 'More than one network returned, unsure which to process and return.'
            return routeviews.peeringdb.Network.from_raw(
                response['data'][0]
            )
        except IndexError:
            raise ValueError(f'Network not found, ASN: {asn}')
