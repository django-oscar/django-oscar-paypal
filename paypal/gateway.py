import requests
import time
import urlparse
import urllib

from paypal import exceptions


def post(url, params):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """

    # Ensure all values are bytestrings before passing to urllib
    for k in params.keys():
        if type(params[k]) == unicode:
            params[k] = params[k].encode('utf-8')
    payload = urllib.urlencode(params.items())

    start_time = time.time()
    response = requests.post(
        url, payload,
        headers={'content-type': 'text/namevalue; charset=utf-8'})
    if response.status_code != requests.codes.ok:
        raise exceptions.PayPalError("Unable to communicate with PayPal")

    # Convert response into a simple key-value format
    pairs = {}
    for key, values in urlparse.parse_qs(response.content).items():
        pairs[key.decode('utf-8')] = values[0].decode('utf-8')

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.content
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
