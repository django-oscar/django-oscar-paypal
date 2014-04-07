import requests
import time
import urlparse

from paypal import exceptions


def post(url, params):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """
    for k in params.keys():
        if type(params[k]) == unicode:
            params[k] = params[k].encode('utf-8')

    # paylfow is not expecting urlencoding (e.g. %, +), therefore don't use urllib.urlencode().
    payload = '&'.join(['%s=%s' % (key, val) for (key, val) in params.items()])

    start_time = time.time()
    response = requests.post(url, payload, headers={'content-type': 'text/namevalue; charset=utf-8'})
    if response.status_code != requests.codes.ok:
        raise exceptions.PayPalError("Unable to communicate with PayPal")

    # Convert response into a simple key-value format
    pairs = {}
    for key, values in urlparse.parse_qs(response.content).items():
        pairs[key] = values[0]

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.content
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
