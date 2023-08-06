import logging
import os
from dataclasses import dataclass
from typing import List

from routeviews import ansible, const, peeringdb, types, yaml

logger = logging.getLogger(__name__)

def load(ansible_inventory_directory: str):
    return Inventory.load(ansible_inventory_directory)

@dataclass
class Inventory:
    collector_configs: List['ansible.CollectorConfig']

    def get_collector_by(self, ipaddr: types.IPAddr) -> 'ansible.CollectorConfig':
        def match(collector_config: 'ansible.CollectorConfig'):
            return ipaddr in collector_config.peerable_ipaddrs

        return next(filter(match, self.collector_configs), None)

    def peer_requests(self, requests: List[peeringdb.PeerRequest]):
        """Add many peer requests to this Inventory in memory.

        > NOTE: Filesystem is not updated until a future call to 'save'.

        Args:
            requests (peeringdb.PeerRequest): The requests to be added.
        """
        return list(map(self.peer_request, requests))

    def peer_request(self, request: peeringdb.PeerRequest):
        """Add a peer request to this Inventory in memory.

        > NOTE: Filesystem is not updated until a future call to 'save'.

        Args:
            request (peeringdb.PeerRequest): The request to be added.
        """
        collector = self.get_collector_by(request.my_address)
        if not collector:
            logger.warning(f'Skipping peer request -- cannot find collector with address: {request.my_address}')
            return
        if collector.is_peered_with(request.your_address):
            logger.info(f'Skipping peer request that already exist: {request.your_address}')
            return
        return collector.add_neighbor(
            asn=request.your_network.asn,
            address=request.your_address,
            description=request.your_network.name,
        )

    def diff(self) -> str:
        messages = []
        for collector in self.collector_configs:
            messages.append(collector.diff())
        messages = filter(lambda message: message.strip() != '', messages)
        final_message = '\n\n'.join(messages)
        if not final_message:
            final_message = '[no changes]'
        return final_message

    @classmethod
    def load(cls, inventory_path: str) -> 'Inventory':
        """Parses all existing YAML config files relating to different collectors.

        Args:
            inventory_path (str): Path to Ansible Inventory.

        Returns:
            Inventory: The inventory loaded into memory.
        """
        return Inventory(
            collector_configs=Inventory.load_collector_configs(inventory_path),
        )

    def save(self):
        """Save all changes back to the Inventory on the filesystem.
        """
        list(map(ansible.CollectorConfig.save, self.collector_configs))

    @staticmethod
    def load_collector_configs(inventory_path) -> List[ansible.CollectorConfig]:
        configs = []
        host_vars_dir = os.path.join(inventory_path, 'host_vars')
        for config_filename in os.listdir(host_vars_dir):
            if not config_filename.startswith(const.ANSIBLE_HOSTVAR_COLLECTOR_FILENAME_PREFIX):
                continue
            config_path = os.path.join(host_vars_dir, config_filename)
            configs.append(ansible.CollectorConfig.load(config_path))
        return configs

    def potential_peer_requests(self, asn: int) -> List[peeringdb.PeerRequest]:
        routeviews_network = peeringdb.get_routeviews_info()
        requestor_network = peeringdb.get_network_info(asn)
        return routeviews_network.potential_peerings_with_network(requestor_network)


# TODO This may be valid
def write_configs(peers_to_write):
    '''
        name, new_peer, config = ptw
        config_name, neighbor, config_itself

    '''
    #  Walk through configs and make sure the peers aren't already configured
    prior_id = None
    for ptw in peers_to_write:
        # TODO Extract below logic to enable config.add_neighbor(neighbor: PeeringDBRouter)
        # config: CollectorConfig

        name, new_peer, config = ptw
        peer_configured = False
        # If we've never seen this config before, then pop the file_path...
        if not prior_id == id(config):
            prior_id = id(config)
            file_path = config.get('file_path')

        # Create 'neighbors' if they don't already exist.
        if 'neighbors' not in config:
            config['neighbors'] = []

        for neighbor in config['neighbors']:
            if neighbor['peer_address'] == new_peer['peer_address']:
                peer_configured = True
                break
        if not peer_configured and 'peer_address' in new_peer:
            config['neighbors'].append(dict(new_peer))
            print(f"writing config to file {file_path}")

            with open(file_path, 'r+') as file:
                yaml.dump(config, file)
            print(
                f"done. check {file_path} and confirm the peer has been added correctly.")
        else:
            print(
                f"peer {new_peer['peer_address']:<24} is already configured. skipping.")
