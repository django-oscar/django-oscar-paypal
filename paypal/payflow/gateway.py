"""
Gateway module - this module should be ignorant of Oscar and could be used in a
non-Oscar project.  All Oscar-related functionality should be in the facade.
"""
import logging

from django.conf import settings

from paypal import gateway
from paypal.payflow import models
from paypal.payflow import codes

logger = logging.getLogger('paypal.payflowpro')

# Payment methods (TENDER)
BANKCARD, PAYPAL = 'C', 'P'


def authorize(card_number, cvv, expiry_date, amt, **kwargs):
    """
    Make an AUTHORIZE request.  This holds the money on the bankcard but doesn't
    actually settle - that comes from a later step.
    """
    params = {
        'TRXTYPE': codes.AUTHORIZATION,
        'TENDER': BANKCARD,
        'AMT': amt,
        # Bankcard
        'ACCT': card_number,
        'CVV2': cvv,
        'EXPDATE': expiry_date,
        # Audit information
        'COMMENT1': kwargs.get('comment1', ''),
        'COMMENT2': kwargs.get('comment2', ''),
        # TODO - Address
        'FIRSTNAME': '',
        'LASTNAME': '',
        'STREET': '',
        'CITY': '',
        'STATE': '',
        'ZIP': '',
    }
    return transaction(params)


def transaction(extra_params):
    # Validate constraints on parameters
    constraints = {
        codes.AUTHORIZATION: ('ACCT', 'AMT', 'EXPDATE'),
    }
    for key in constraints[extra_params['TRXTYPE']]:
        if key not in extra_params:
            raise RuntimeError("The key %s must be supplied" % key)

    params = {
        # Required user params
        'USER': settings.PAYPAL_PAYFLOW_USER,
        'VENDOR': settings.PAYPAL_PAYFLOW_VENDOR_ID,
        'PARTNER': settings.PAYPAL_PAYFLOW_PARTNER_ID,
        'PWD': settings.PAYPAL_PAYFLOW_PASSWORD,
    }
    params.update(extra_params)

    if settings.PAYPAL_PAYFLOW_TEST_MODE:
        url = 'https://pilot-payflowpro.paypal.com'
    else:
        url = 'https://payflowpro.paypal.com'

    pairs = gateway.post(url, params)

    # Create transaction model
    return models.PayflowTransaction.objects.create(
        trxtype=params['TRXTYPE'],
        tender=params['TENDER'],
        amount=params['AMT'],
        pnref=pairs.get('PNREF', None),
        ppref=pairs.get('PPREF', None),
        cvv2match=pairs.get('CVV2MATCH', None),
        result=pairs.get('RESULT', None),
        respmsg=pairs.get('RESPMSG', None),
        authcode=pairs.get('AUTHCODE', None),
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time']
    )
