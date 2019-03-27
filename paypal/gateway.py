from __future__ import unicode_literals

import time

import requests
from django.utils import six
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import parse_qsl

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
    for key, value in parse_qsl(response.text):
        if isinstance(key, six.binary_type):
            key = key.decode('utf8')
        if isinstance(value, six.binary_type):
            value = value.decode('utf8')
        pairs[key] = value

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.text
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
