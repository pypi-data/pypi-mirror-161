"""Anonymous getter functions, to get data from PeeringDB (without an account).
"""
import logging

import routeviews.const
import routeviews.peeringdb

logger = logging.getLogger(__name__)


# Establish a single repository, for anonymous access to PeeringDB.
def _peeringdb_repo() -> 'routeviews.peeringdb.Repository':
    if routeviews.peeringdb.Repository.instances:
        repo = routeviews.peeringdb.Repository.instances[-1]
        logger.debug(f'Using PeeringDB account: {repo.username}')
        return routeviews.peeringdb.Repository.instances[-1]
    return routeviews.peeringdb.Repository()


def get_network_info(network_asn: int) -> 'routeviews.peeringdb.Network':
    """See :func:`~routeviews.peeringdb.Repository.get_network_info`.
    """
    return _peeringdb_repo().get_network_info(network_asn)


def get_routeviews_info() -> 'routeviews.peeringdb.Network':
    """See :func:`~routeviews.peeringdb.Repository.get_network_info`.
    """
    return _peeringdb_repo().get_network_info(routeviews.const.ASN)
