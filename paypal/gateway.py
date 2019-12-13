import time
from urllib.parse import parse_qsl

import requests
from django.utils.http import urlencode

from paypal import exceptions


def post(url, params, encode=True):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """
    if encode:
        payload = urlencode(params)
    else:
        payload = params

    start_time = time.time()
    response = requests.post(
        url, payload,
        headers={'content-type': 'text/namevalue; charset=utf-8'})
    if response.status_code != requests.codes.ok:
        raise exceptions.PayPalError("Unable to communicate with PayPal")

    # Convert response into a simple key-value format
    pairs = {}
    for key, value in parse_qsl(response.text):
        pairs[key] = value

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.text
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
