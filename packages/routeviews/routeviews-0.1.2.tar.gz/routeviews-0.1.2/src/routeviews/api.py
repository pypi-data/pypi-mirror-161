import requests


def get_info(collector):
    # Format the collector name -- omit the 
    name = collector.replace('.routeviews.org', '')
    c_data = requests.get(f'https://api.routeviews.org/collector/?name={name}')
    return c_data.json()['results'][0]
