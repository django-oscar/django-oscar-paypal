"""
Adaptive payments:

https://www.x.com/developers/paypal/documentation-tools/adaptive-payments/gs_AdaptivePayments
"""
import json
import requests
import collections
from decimal import Decimal as D
from django.conf import settings

from paypal import gateway, models

Receiver = collections.namedtuple('Receiver', 'email amount is_primary')

# Enum class for who pays the fees
# See pg 80 of the guide
Fees = type('Feeds', (), {
    'SENDER': 'SENDER',
    'PRIMARY_RECEIVER': 'PRIMARYRECEIVER',
    'EACH_RECEIVER': 'EACHRECIEVER',
    'SECONDARY_ONLY': 'SECONDARYONLY',
})


def pay(receivers, currency, return_url, cancel_url,
        ip_address, tracking_id=None, fees_payer=None,
        memo=None):
    """
    Submit a 'Pay' transaction to PayPal
    """
    headers = {
        'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_API_USERNAME,
        'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_API_PASSWORD,
        'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_API_SIGNATURE,
        'X-PAYPAL-APPLICATION-ID': settings.PAYPAL_API_APPLICATION_ID,
        # Use NVP so we can re-used code from Expres and Payflow Pro
        'X-PAYPAL-REQUEST-DATA-FORMAT': 'NV',
        'X-PAYPAL-RESPONSE-DATA-FORMAT': 'NV',
        'X-PAYPAL-DEVICE-IPADDRESS': ip_address,
    }
    # Set core params
    action = "PAY"
    params = [
        ("actionType", action),
        ("currencyCode", currency),
        ("returnUrl", return_url),
        ("cancelUrl", cancel_url),
        ("requestEnvelope.errorLanguage", "en_US"),
        ("requestEnvelope.detailLevel", "ReturnAll"),
    ]
    for index, receiver in enumerate(receivers):
        params.append(('receiverList.receiver(%d).amount' % index,
                       str(receiver.amount)))
        params.append(('receiverList.receiver(%d).email' % index,
                       receiver.email))
        params.append(('receiverList.receiver(%d).primary' % index,
                       'true' if receiver.is_primary else 'false'))
    # Add optional params
    if fees_payer:
        params.append(('feesPayer', fees_payer))
    if tracking_id:
        params.append(('trackingId', tracking_id))
    if memo:
        params.append(('memo', memo))

    if getattr(settings, 'PAYPAL_SANDBOX_MODE', False):
        url = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Pay'
        is_sandbox = True
    else:
        url = 'https://svcs.paypal.com/AdaptivePayments/Pay'
        is_sandbox = False

    # We use an OrderedDict as the key-value pairs have to be in the correct
    # order(!).  Otherwise, PayPal returns error 'Invalid request: {0}'
    # with errorId 580001.  All very silly.
    pairs = gateway.post(url, collections.OrderedDict(params), headers)

    # Create model that represents request/response
    return models.AdaptiveTransaction.objects.create(
        is_sandbox=is_sandbox,
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time'],
        action=action,
        currency=currency,
        ack=pairs.get('responseEnvelope.ack', None),
        pay_key=pairs.get('payKey', None),
        correlation_id=pairs.get('responseEnvelope.correlationId', None),
        error_id=pairs.get('error(0).errorId', None),
        error_message=pairs.get('error(0).message', None))
