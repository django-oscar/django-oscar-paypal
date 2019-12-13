"""
Gateway module - this module should be ignorant of Oscar and could be used in a
non-Oscar project.  All Oscar-related functionality should be in the facade.
"""
import logging

from django.conf import settings
from django.core import exceptions

from paypal import gateway
from paypal.payflow import codes, models

logger = logging.getLogger('paypal.payflow')


def authorize(order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Make an AUTHORIZE request.

    This holds the money within the customer's bankcard but doesn't
    actually settle - that comes from a later step.

    * The hold lasts for around a week.
    * The hold cannot be cancelled through the PayPal API.
    """
    return _submit_payment_details(codes.AUTHORIZATION, order_number, card_number, cvv, expiry_date,
                                   amt, **kwargs)


def sale(order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Make a SALE request.

    This authorises money within the customer's bank and marks it for settlement
    immediately.
    """
    return _submit_payment_details(codes.SALE, order_number, card_number, cvv, expiry_date,
                                   amt, **kwargs)


def _submit_payment_details(trxtype, order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Submit payment details to PayPal.
    """
    params = {
        'TRXTYPE': trxtype,
        'TENDER': codes.BANKCARD,
        'AMT': amt,
        # Bankcard
        'ACCT': card_number,
        'CVV2': cvv,
        'EXPDATE': expiry_date,
        # Audit information (eg order number)
        'COMMENT1': order_number,
        'COMMENT2': kwargs.get('comment2', ''),
        # Billing address (only required if using address verification service)
        'FIRSTNAME': kwargs.get('first_name', ''),
        'LASTNAME': kwargs.get('last_name', ''),
        'STREET': kwargs.get('street', ''),
        'CITY': kwargs.get('city', ''),
        'STATE': kwargs.get('state', ''),
        'ZIP': kwargs.get('zip', ''),
        'BILLTOCOUNTRY': kwargs.get('countrycode', ''),
        'EMAIL': kwargs.get('user_email', ''),
        'PHONENUM': kwargs.get('billing_phone_number', ''),
    }

    # Allow inclusion of optional parameters in transactions such as:
    # dict(shipto_first_name='SHIPTOFIRSTNAME', ...)
    #   OR
    # dict(bncode='BUTTONSOURCE', ...)
    OPTIONAL_PARAMS = getattr(settings, 'PAYPAL_PAYFLOW_OPTIONAL_PARAMS', dict())
    if isinstance(OPTIONAL_PARAMS, dict):
        # add optional parameters here
        for key, name in OPTIONAL_PARAMS.items():
            value = kwargs.get(key)
            if value:
                params.update({'{}'.format(name): value})
    return _transaction(params)


def delayed_capture(order_number, pnref, amt=None):
    """
    Perform a DELAYED CAPTURE transaction.

    This captures money that was previously authorised.
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.DELAYED_CAPTURE,
        'ORIGID': pnref
    }
    if amt:
        params['AMT'] = amt
    return _transaction(params)


def reference_transaction(order_number, pnref, amt):
    """
    Capture money using the card/address details of a previous transaction

    * The PNREF of the original txn is valid for 12 months
    """
    params = {
        'COMMENT1': order_number,
        # Use SALE as we are effectively authorising and settling a new
        # transaction
        'TRXTYPE': codes.SALE,
        'TENDER': codes.BANKCARD,
        'ORIGID': pnref,
        'AMT': amt,
    }
    return _transaction(params)


def credit(order_number, pnref, amt=None):
    """
    Refund money back to a bankcard.
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.CREDIT,
        'ORIGID': pnref
    }
    if amt:
        params['AMT'] = amt
    return _transaction(params)


def void(order_number, pnref):
    """
    Prevent a transaction from being settled
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.VOID,
        'ORIGID': pnref
    }
    return _transaction(params)


def _transaction(extra_params):
    """
    Perform a transaction with PayPal.

    :extra_params: Additional parameters to include in the payload other than
    the user credentials.
    """
    if 'TRXTYPE' not in extra_params:
        raise RuntimeError("All transactions must specify a 'TRXTYPE' paramter")

    # Validate constraints on parameters
    constraints = {
        codes.AUTHORIZATION: ('ACCT', 'AMT', 'EXPDATE'),
        codes.SALE: ('AMT',),
        codes.DELAYED_CAPTURE: ('ORIGID',),
        codes.CREDIT: ('ORIGID',),
        codes.VOID: ('ORIGID',),
    }
    trxtype = extra_params['TRXTYPE']
    for key in constraints[trxtype]:
        if key not in extra_params:
            raise RuntimeError(
                "A %s parameter must be supplied for a %s transaction" % (
                    key, trxtype))

    # At a minimum, we require a vendor ID and a password.
    for setting in ('PAYPAL_PAYFLOW_VENDOR_ID',
                    'PAYPAL_PAYFLOW_PASSWORD'):
        if not hasattr(settings, setting):
            raise exceptions.ImproperlyConfigured(
                "You must define a %s setting" % setting
            )

    # Set credentials
    params = {
        'VENDOR': settings.PAYPAL_PAYFLOW_VENDOR_ID,
        'PWD': settings.PAYPAL_PAYFLOW_PASSWORD,
        'USER': getattr(settings, 'PAYPAL_PAYFLOW_USER',
                        settings.PAYPAL_PAYFLOW_VENDOR_ID),
        'PARTNER': getattr(settings, 'PAYPAL_PAYFLOW_PARTNER',
                           'PayPal')
    }
    params.update(extra_params)

    # Ensure that any amounts have a currency and are formatted correctly
    if 'AMT' in params:
        if 'CURRENCY' not in params:
            params['CURRENCY'] = getattr(settings,
                                         'PAYPAL_PAYFLOW_CURRENCY', 'USD')
        params['AMT'] = "%.2f" % params['AMT']

    if getattr(settings, 'PAYPAL_PAYFLOW_PRODUCTION_MODE', False):
        url = 'https://payflowpro.paypal.com'
    else:
        url = 'https://pilot-payflowpro.paypal.com'

    logger.info("Performing %s transaction (trxtype=%s)",
                codes.trxtype_map[trxtype], trxtype)
    pairs = gateway.post(
        url,
        '&'.join(['{}={}'.format(n, v) for n, v in params.items()]),
        encode=False
    )

    # Beware - this log information will contain the Payflow credentials
    # only use it in development, not production.
    logger.debug("Raw request: %s", pairs['_raw_request'])
    logger.debug("Raw response: %s", pairs['_raw_response'])

    return models.PayflowTransaction.objects.create(
        comment1=params['COMMENT1'],
        trxtype=params['TRXTYPE'],
        tender=params.get('TENDER', None),
        amount=params.get('AMT', None),
        pnref=pairs.get('PNREF', None),
        ppref=pairs.get('PPREF', None),
        cvv2match=pairs.get('CVV2MATCH', None),
        avsaddr=pairs.get('AVSADDR', None),
        avszip=pairs.get('AVSZIP', None),
        result=pairs.get('RESULT', None),
        respmsg=pairs.get('RESPMSG', None),
        authcode=pairs.get('AUTHCODE', None),
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time']
    )
