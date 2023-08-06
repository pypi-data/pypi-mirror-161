"""Route Views *constant* values to be used throughout codebase (and never changed).
"""

# BGP AFI/SAFI values
IPV4_UNICAST_AFI_SAFI = 'ipv4_unicast'
IPV6_UNICAST_AFI_SAFI = 'ipv6_unicast'


# Route Views' ASN
ASN = 6447


# All Ansible hostvar files for 'collectors' start with this string
# TODO, document this key naming convention
ANSIBLE_HOSTVAR_COLLECTOR_FILENAME_PREFIX = 'route-views'


# TODO, remove this and push into inventory instead somehow. (e.g. new group makes sense to me)
MULTIHOP_COLLECTORS = [
    'route-views.routeviews.org',
    'route-views2.routeviews.org',
    'route-views3.routeviews.org',
    'route-views4.routeviews.org',
    'route-views5.routeviews.org',
    'route-views6.routeviews.org',
]


ADDPATH_COLLECTORS = [
    'route-views7.routeviews.org',
]
