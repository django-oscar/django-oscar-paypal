import urllib
import logging
from decimal import Decimal as D

from django.conf import settings
from django.template.defaultfilters import truncatewords

from paypal.express import models
from paypal import gateway
from paypal import exceptions


# PayPal methods
SET_EXPRESS_CHECKOUT = 'SetExpressCheckout'
GET_EXPRESS_CHECKOUT = 'GetExpressCheckoutDetails'
DO_EXPRESS_CHECKOUT = 'DoExpressCheckoutPayment'
DO_CAPTURE = 'DoCapture'
DO_VOID = 'DoVoid'
REFUND_TRANSACTION = 'RefundTransaction'

SALE, AUTHORIZATION, ORDER = 'Sale', 'Authorization', 'Order'

# It's quite difficult to work out what the latest version of the PayPal Express
# API is.  The best way is to look for the 'web version: ...' string in the
# source of https://www.sandbox.paypal.com/
API_VERSION = getattr(settings, 'PAYPAL_API_VERSION', '88.0')

logger = logging.getLogger('paypal.express')


def _fetch_response(method, extra_params):
    """
    Fetch the response from PayPal and return a transaction object
    """
    # Build parameter string
    params = {
        'METHOD': method,
        'VERSION': API_VERSION,
        'USER': settings.PAYPAL_API_USERNAME,
        'PWD': settings.PAYPAL_API_PASSWORD,
        'SIGNATURE': settings.PAYPAL_API_SIGNATURE,
    }
    params.update(extra_params)

    if getattr(settings, 'PAYPAL_SANDBOX_MODE', True):
        url = 'https://api-3t.sandbox.paypal.com/nvp'
    else:
        url = 'https://api-3t.paypal.com/nvp'
    pairs = gateway.post(url, params)

    # Record transaction data - we save this model whether the txn
    # was successful or not
    txn = models.ExpressTransaction(
        method=method,
        version=API_VERSION,
        ack=pairs['ACK'],
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time'],
    )
    if txn.is_successful:
        txn.correlation_id = pairs['CORRELATIONID']
        if method == SET_EXPRESS_CHECKOUT:
            txn.amount = params['PAYMENTREQUEST_0_AMT']
            txn.currency = params['PAYMENTREQUEST_0_CURRENCYCODE']
            txn.token = pairs['TOKEN']
        elif method == GET_EXPRESS_CHECKOUT:
            txn.token = params['TOKEN']
            txn.amount = D(pairs['PAYMENTREQUEST_0_AMT'])
            txn.currency = pairs['PAYMENTREQUEST_0_CURRENCYCODE']
        elif method == DO_EXPRESS_CHECKOUT:
            txn.token = params['TOKEN']
            txn.amount = D(pairs['PAYMENTINFO_0_AMT'])
            txn.currency = pairs['PAYMENTINFO_0_CURRENCYCODE']
    else:
        if 'L_ERRORCODE0' in pairs:
            txn.error_code = pairs['L_ERRORCODE0']
        if 'L_LONGMESSAGE0' in pairs:
            txn.error_message = pairs['L_LONGMESSAGE0']
    txn.save()

    if not txn.is_successful:
        msg = "Error %s - %s" % (txn.error_code, txn.error_message)
        logger.error(msg)
        raise exceptions.PayPalError(msg)

    return txn


def set_txn(basket, shipping_methods, currency, return_url, cancel_url, update_url=None,
            action=SALE, user=None, user_address=None, shipping_method=None,
            shipping_address=None):
    """
    Register the transaction with PayPal to get a token which we use in the
    redirect URL.  This is the 'SetExpressCheckout' from their documentation.

    There are quite a few options that can be passed to PayPal to configure this
    request - most are controlled by PAYPAL_* settings.
    """
    # PayPal have an upper limit on transactions.  It's in dollars which is
    # a fiddly to work with.  Lazy solution - only check when dollars are used as
    # the PayPal currency.
    amount = basket.total_incl_tax
    if currency == 'USD' and amount > 10000:
        raise exceptions.PayPalError('PayPal can only be used for orders up to 10000 USD')

    params = {
        'PAYMENTREQUEST_0_AMT': amount,
        'PAYMENTREQUEST_0_CURRENCYCODE': currency,
        'RETURNURL': return_url,
        'CANCELURL': cancel_url,
        'PAYMENTREQUEST_0_PAYMENTACTION': action,
    }

    # Add item details
    for index, line in enumerate(basket.all_lines()):
        product = line.product
        params['L_PAYMENTREQUEST_0_NAME%d' % index] = product.get_title()
        params['L_PAYMENTREQUEST_0_NUMBER%d' % index] = product.upc
        params['L_PAYMENTREQUEST_0_DESC%d' % index] = truncatewords(product.description, 12)
        params['L_PAYMENTREQUEST_0_AMT%d' % index] = line.unit_price_incl_tax
        params['L_PAYMENTREQUEST_0_QTY%d' % index] = line.quantity

    # We include tax in the prices rather than separately as that's how it's
    # done on most British/Australian sites.  Will need to refactor in the
    # future no doubt
    params['PAYMENTREQUEST_0_ITEMAMT'] = basket.total_incl_tax
    params['PAYMENTREQUEST_0_TAXAMT'] = D('0.00')

    # Customer services number
    customer_service_num = getattr(settings, 'PAYPAL_CUSTOMER_SERVICES_NUMBER', None)
    if customer_service_num:
        params['CUSTOMERSERVICENUMBER'] = customer_service_num

    # Display settings
    page_style = getattr(settings, 'PAYPAL_PAGESTYLE', None)
    header_image = getattr(settings, 'PAYPAL_HEADER_IMG', None)
    if page_style:
        params['PAGESTYLE'] = page_style
    elif header_image:
        params['LOGOIMG'] = header_image
    else:
        # Think these settings maybe deprecated in latest version of PayPal's API
        display_params = {
            'HDRBACKCOLOR': getattr(settings, 'PAYPAL_HEADER_BACK_COLOR', None),
            'HDRBORDERCOLOR': getattr(settings, 'PAYPAL_HEADER_BORDER_COLOR', None),
        }
        params.update(x for x in display_params.items() if bool(x[1]))

    # Locale
    locale = getattr(settings, 'PAYPAL_LOCALE', None)
    if locale:
        valid_choices = ('AU', 'DE', 'FR', 'GB', 'IT', 'ES', 'JP', 'US')
        if locale not in valid_choices:
            raise ImproperlyConfigured("'%s' is not a valid locale code" % locale)
        params['LOCALECODE'] = locale

    # Confirmed shipping address
    confirm_shipping_addr = getattr(settings, 'PAYPAL_CONFIRM_SHIPPING', None)
    if confirm_shipping_addr:
        params['REQCONFIRMSHIPPING'] = 1

    # Instant update callback information
    if update_url:
        params['CALLBACK'] = update_url
        params['CALLBACKTIMEOUT'] = getattr(settings, 'PAYPAL_CALLBACK_TIMEOUT', 3)

    # Contact details and address details - we provide these as it would make the PayPal
    # registration process smoother is the user doesn't already have an account.
    if user:
        params['EMAIL'] = user.email
    if user_address:
        params['SHIPTOSTREET'] = user_address.line1
        params['SHIPTOSTREET2'] = user_address.line2
        params['SHIPTOCITY'] = user_address.line4
        params['SHIPTOSTATE'] = user_address.state
        params['SHIPTOZIP'] = user_address.postcode
        params['SHIPTOCOUNTRYCODE'] = user_address.country.iso_3166_1_a2

    # Shipping details (if already set) - we override the SHIPTO* fields
    # and set a flag to indicate that these can't be altered on the PayPal side.
    if shipping_method and shipping_address:
        params['ADDROVERRIDE'] = 1
        # It's recommend not to set 'confirmed shipping' if supplying the shipping
        # address directly.
        params['REQCONFIRMSHIPPING'] = 0
        params['SHIPTOSTREET'] = shipping_address.line1
        params['SHIPTOSTREET2'] = shipping_address.line2
        params['SHIPTOCITY'] = shipping_address.line4
        params['SHIPTOSTATE'] = shipping_address.state
        params['SHIPTOZIP'] = shipping_address.postcode
        params['SHIPTOCOUNTRYCODE'] = shipping_address.country.iso_3166_1_a2

    # Allow customer to specify a shipping note
    allow_note = getattr(settings, 'PAYPAL_ALLOW_NOTE', True)
    if allow_note:
        params['ALLOWNOTE'] = 1

    # Shipping charges
    params['PAYMENTREQUEST_0_SHIPPINGAMT'] = D('0.00')
    max_charge = D('0.00')
    for index, method in enumerate(shipping_methods):
        is_default = index == 0
        params['L_SHIPPINGOPTIONISDEFAULT%d' % index] = 'true' if is_default else 'false'
        charge = method.basket_charge_incl_tax()
        if charge > max_charge:
            max_charge = charge
        if is_default:
            params['PAYMENTREQUEST_0_SHIPPINGAMT'] = charge
        params['L_SHIPPINGOPTIONNAME%d' % index] = method.name
        params['L_SHIPPINGOPTIONAMOUNT%d' % index] = charge

    # Set shipping charge explicitly if it has been passed
    if shipping_method:
        max_charge = charge = shipping_method.basket_charge_incl_tax()
        params['PAYMENTREQUEST_0_SHIPPINGAMT'] = charge
        params['PAYMENTREQUEST_0_AMT'] += charge

    # Both the old version (MAXAMT) and the new version (PAYMENT...) are needed
    # here - think it's a problem with the API.
    params['PAYMENTREQUEST_0_MAXAMT'] = amount + max_charge
    params['MAXAMT'] = amount + max_charge

    # Handling set to zero for now - I've never worked on a site that needed a
    # handling charge.
    params['PAYMENTREQUEST_0_HANDLINGAMT'] = D('0.00')

    txn = _fetch_response(SET_EXPRESS_CHECKOUT, params)

    # Construct return URL
    if getattr(settings, 'PAYPAL_SANDBOX_MODE', True):
        url = 'https://www.sandbox.paypal.com/webscr'
    else:
        url = 'https://www.paypal.com/webscr'
    params = (('cmd', '_express-checkout'),
              ('token', txn.token),)
    return '%s?%s' % (url, urllib.urlencode(params))


def get_txn(token):
    """
    Fetch details of a transaction from PayPal using the token as
    an identifier.
    """
    return _fetch_response(GET_EXPRESS_CHECKOUT, {'TOKEN': token})


def do_txn(payer_id, token, amount, currency, action=SALE):
    """
    DoExpressCheckoutPayment
    """
    params = {
        'PAYERID': payer_id,
        'TOKEN': token,
        'PAYMENTREQUEST_0_AMT': amount,
        'PAYMENTREQUEST_0_CURRENCYCODE': currency,
        'PAYMENTREQUEST_0_PAYMENTACTION': action,
    }
    return _fetch_response(DO_EXPRESS_CHECKOUT, params)


def do_capture(txn_id, amount, currency, complete_type='Complete',
               note=None):
    """
    Capture payment from a previous transaction

    See https://cms.paypal.com/uk/cgi-bin/?&cmd=_render-content&content_ID=developer/e_howto_api_soap_r_DoCapture
    """
    params = {
        'AUTHORIZATIONID': txn_id,
        'AMT': amount,
        'CURRENCYCODE': currency,
        'COMPLETETYPE': complete_type,
    }
    if note:
        params['NOTE'] = note
    return _fetch_response(DO_CAPTURE, params)


def do_void(txn_id, note=None):
    params = {
        'AUTHORIZATIONID': txn_id,
    }
    if note:
        params['NOTE'] = note
    return _fetch_response(DO_VOID, params)


FULL_REFUND = 'Full'
PARTIAL_REFUND = 'Partial'
def refund_txn(txn_id, is_partial=False, amount=None, currency=None):
    params = {
        'TRANSACTIONID': txn_id,
        'REFUNDTYPE': PARTIAL_REFUND if is_partial else FULL_REFUND,
    }
    if is_partial:
        params['AMT'] = amount
        params['CURRENCYCODE'] = currency
    return _fetch_response(REFUND_TRANSACTION, params)
