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

# Custom tuple for submitting receiver information
Receiver = collections.namedtuple('Receiver', 'email amount is_primary')

# Enum class for who pays the fees
# See pg 80 of the guide
Fees = type('Feeds', (), {
    'SENDER': 'SENDER',
    'PRIMARY_RECEIVER': 'PRIMARYRECEIVER',
    'EACH_RECEIVER': 'EACHRECEIVER',
    'SECONDARY_ONLY': 'SECONDARYONLY',
})


def payment_details(pay_key):
    """
    Fetch the payment details for a given transaction
    """
    params = [("payKey", pay_key),]
    return _request('PaymentDetails', params)


def pay(receivers, currency, return_url, cancel_url,
        ip_address, tracking_id=None, fees_payer=None,
        memo=None):
    """
    Submit a 'Pay' transaction to PayPal
    """
    headers = {
        'X-PAYPAL-DEVICE-IPADDRESS': ip_address,
    }
    # Set core params
    action = "Pay"
    params = [
        ("actionType", action.upper()),
        ("currencyCode", currency),
        ("returnUrl", return_url),
        ("cancelUrl", cancel_url),
    ]
    total = D('0.00')
    for index, receiver in enumerate(receivers):
        params.append(('receiverList.receiver(%d).amount' % index,
                       str(receiver.amount)))
        params.append(('receiverList.receiver(%d).email' % index,
                       receiver.email))
        params.append(('receiverList.receiver(%d).primary' % index,
                       'true' if receiver.is_primary else 'false'))
        # The primary receiver should have the total amount as their amount
        if receiver.is_primary:
            total = receiver.amount
    # Add optional params
    if fees_payer:
        params.append(('feesPayer', fees_payer))
    if tracking_id:
        params.append(('trackingId', tracking_id))
    if memo:
        params.append(('memo', memo))

    # We pass the total so it can be added to the txn model for better audit
    return _request(action, params, headers, {'amount': total})


def _request(action, params, headers=None, txn_fields=None):
    """
    Make a request to PayPal
    """
    if headers is None:
        headers = {}
    if txn_fields is None:
        txn_fields = {}
    request_headers = {
        'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_API_USERNAME,
        'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_API_PASSWORD,
        'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_API_SIGNATURE,
        'X-PAYPAL-APPLICATION-ID': settings.PAYPAL_API_APPLICATION_ID,
        # Use NVP so we can re-used code from Express and Payflow Pro
        'X-PAYPAL-REQUEST-DATA-FORMAT': 'NV',
        'X-PAYPAL-RESPONSE-DATA-FORMAT': 'NV',
    }
    request_headers.update(headers)

    common_params = [
        ("requestEnvelope.errorLanguage", "en_US"),
        ("requestEnvelope.detailLevel", "ReturnAll"),
    ]
    params.extend(common_params)

    if getattr(settings, 'PAYPAL_SANDBOX_MODE', False):
        url = 'https://svcs.sandbox.paypal.com/AdaptivePayments/%s'
        is_sandbox = True
    else:
        url = 'https://svcs.paypal.com/AdaptivePayments/%s'
        is_sandbox = False
    url = url % action

    # We use an OrderedDict as the key-value pairs have to be in the correct
    # order(!).  Otherwise, PayPal returns error 'Invalid request: {0}'
    # with errorId 580001.  All very silly.
    pairs = gateway.post(url, collections.OrderedDict(params), request_headers)

    # Create model that represents request/response
    return models.AdaptiveTransaction.objects.create(
        action=action,
        is_sandbox=is_sandbox,
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time'],
        currency=pairs.get('currencyCode', None),
        ack=pairs.get('responseEnvelope.ack', None),
        pay_key=pairs.get('payKey', None),
        correlation_id=pairs.get('responseEnvelope.correlationId', None),
        error_id=pairs.get('error(0).errorId', None),
        error_message=pairs.get('error(0).message', None),
        **txn_fields)
