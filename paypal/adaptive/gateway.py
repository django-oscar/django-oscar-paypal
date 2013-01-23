"""
Adaptive payments:

https://www.x.com/developers/paypal/documentation-tools/adaptive-payments/gs_AdaptivePayments
"""
import json
import requests
import collections
from decimal import Decimal as D

Receiver = collections.namedtuple('Receiver', 'email amount')


def pay(user_id, password, signature, application_id):

    # Params
    action = 'PAY'
    currency = 'CCH'
    return_url = 'http://example.com/success/'
    cancel_url = 'http://example.com/cancel/'
    receivers = (
        Receiver(email='a@a.com', amount=D('12.00')),
        Receiver(email='b@a.com', amount=D('1.00')),
    )

    headers = {
        'X-PAYPAL-SECURITY-USERID': user_id,
        'X-PAYPAL-SECURITY-PASSWORD': password,
        'X-PAYPAL-SECURITY-SIGNATURE': signature,
        'X-PAYPAL-APPLICATION-ID': application_id,
        'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
        'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
    }
    payload = {
        "actionType": action,
        "currencyCode": currency,
        "receiverList": {'receiver': []},
        "returnUrl": return_url,
        "cancelUrl": cancel_url,
        "requestEnvelope": {
            "errorLanguage": "en_US",
            "detailLevel":"ReturnAll"
        }
    }
    for receiver in receivers:
        payload['receiverList']['receiver'].append({
            'amount': receiver.amount,
            'email': receiver.email
        })
    response = requests.post(url, data=json.dumps(payload),
                             headers=headers)
