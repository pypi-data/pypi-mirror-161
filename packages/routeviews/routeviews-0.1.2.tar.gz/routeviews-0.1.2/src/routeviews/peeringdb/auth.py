

import logging

logger = logging.getLogger(__name__)

API_KEY_USERNAME = 'Api-Key'


def HTTP_header(username: str = None, password: str = None, api_key: str = None):
    """Generate an HTTP Basic Authorization header.  

    > Prefers API Key over username/password.
    """
    if api_key:
        logger.info('Preferring API Key over username/password.')
        header = f'{API_KEY_USERNAME} {api_key}'
    elif username and password:
        logger.info(f'Authorization via username/password on behalf of {username} (username).')
        header = f'{username} {password}'
    else:
        raise ValueError('Expected username/password or api_key')
    return header
    # It seems peeringDB doesn't support base64 encoded
    # header_bytes = header.encode() 
    # from base64 import b64encode
    # return b64encode(header_bytes) 
