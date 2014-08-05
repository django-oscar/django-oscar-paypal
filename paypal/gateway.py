import requests
import time

from django.utils.encoding import force_text
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import parse_qs

from paypal import exceptions


def post(url, params):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """
    payload = urlencode(params)
    start_time = time.time()
    response = requests.post(
        url, payload,
        headers={'content-type': 'text/namevalue; charset=utf-8'})
    if response.status_code != requests.codes.ok:
        raise exceptions.PayPalError("Unable to communicate with PayPal")

    # Convert response into a simple key-value format
    pairs = {}
    for key, values in parse_qs(response.content).items():
        pairs[force_text(key)] = force_text(values[0])

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.content
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
