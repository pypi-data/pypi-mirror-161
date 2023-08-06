"""Parse bytes or strings returned by PeeringDB API into Python objects.

Parse functions should only ever raise KeyErrors.
Other errors should be handled like so:
    * log at debug level, and 
    * return 'empty' by default. E.g. [], '', {}. (TODO: or return None?)
"""
from datetime import datetime
import logging
from typing import List

# WARNING: Do not reference at module-load time (circular dependency).
import routeviews.peeringdb


PEERINGDB_TIME_FORMAT_STRING = '%Y-%m-%dT%H:%M:%S%z'


logger = logging.getLogger(__name__)


# TODO Move all 'staticmethod' parse functions into here


def DateTime(time: str) -> datetime:
    try:
        return datetime.strptime(time, PEERINGDB_TIME_FORMAT_STRING)
    except ValueError:
        logger.debug(f'Invalid DateTime {time}')


def Contacts(poc_set: List) -> List['routeviews.peeringdb.Contact']:
    try:
        return list(map(
            routeviews.peeringdb.Contact.from_data,
            poc_set
        ))
    except KeyError:
        logger.warning()
        return []


def Routers(netixlan_set) -> List['routeviews.peeringdb.Router']:
    try:
        return list(map(
            routeviews.peeringdb.Router.from_raw,
            netixlan_set
        ))
    except KeyError:
        return []
