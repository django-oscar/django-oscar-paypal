"""
Responsible for bridging between Oscar and the PayPal gateway
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from paypal.express.gateway import (
    AUTHORIZATION, DO_EXPRESS_CHECKOUT, ORDER, SALE, do_capture, do_txn, do_void, get_txn, refund_txn)
from paypal.express.gateway_new import PaymentProcessor
from paypal.express.models import ExpressTransaction as Transaction


def _get_payment_action():
    # PayPal supports 3 actions: 'Sale', 'Authorization', 'Order'
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)
    if action not in (SALE, AUTHORIZATION, ORDER):
        raise ImproperlyConfigured("'%s' is not a valid payment action" % action)
    return action


def get_paypal_url(basket, user=None, shipping_address=None,
                   shipping_method=None, host=None, scheme=None,
                   paypal_params=None):
    """
    Return the URL for a PayPal Express transaction.

    This involves registering the txn with PayPal to get a one-time
    URL.  If a shipping method and shipping address are passed, then these are
    given to PayPal directly - this is used within when using PayPal as a
    payment method.
    """
    if basket.currency:
        currency = basket.currency
    else:
        currency = getattr(settings, 'PAYPAL_CURRENCY', 'GBP')
    if host is None:
        host = Site.objects.get_current().domain
    scheme = getattr(settings, 'PAYPAL_CALLBACK_SCHEME', 'https')
    return_url_path = reverse('paypal-success-response', kwargs={'basket_id': basket.id})
    return_url = '{0}://{1}{2}'.format(scheme, host, return_url_path)

    cancel_url_path = reverse('paypal-cancel-response', kwargs={'basket_id': basket.id})
    cancel_url = '{0}://{1}{2}'.format(scheme, host, cancel_url_path)

    # Determine whether a shipping address is required
    no_shipping = False
    if not basket.is_shipping_required():
        no_shipping = True

    # Pass a default billing address is there is one.  This means PayPal can
    # pre-fill the registration form.
    address = None
    if user:
        addresses = user.addresses.all().order_by('-is_default_for_billing')
        if len(addresses):
            address = addresses[0]

    return PaymentProcessor().create_order(
        basket=basket,
        currency=currency,
        return_url=return_url,
        cancel_url=cancel_url,
        user=user,
        user_address=address,
        shipping_address=shipping_address,
        shipping_method=shipping_method,
        no_shipping=no_shipping,
    )


def fetch_transaction_details(token):
    """
    Fetch the completed details about the PayPal transaction.
    """
    return get_txn(token)


def confirm_transaction(payer_id, token, amount, currency):
    """
    Confirm the payment action.
    """
    return do_txn(payer_id, token, amount, currency,
                  action=_get_payment_action())


def refund_transaction(token, amount, currency, note=None):
    txn = Transaction.objects.get(token=token,
                                  method=DO_EXPRESS_CHECKOUT)
    is_partial = amount < txn.amount
    return refund_txn(txn.value('PAYMENTINFO_0_TRANSACTIONID'), is_partial, amount, currency)


def capture_authorization(token, note=None):
    """
    Capture a previous authorization.
    """
    txn = Transaction.objects.get(token=token,
                                  method=DO_EXPRESS_CHECKOUT)
    return do_capture(txn.value('PAYMENTINFO_0_TRANSACTIONID'),
                      txn.amount, txn.currency, note=note)


def void_authorization(token, note=None):
    """
    Void a previous authorization.
    """
    txn = Transaction.objects.get(token=token,
                                  method=DO_EXPRESS_CHECKOUT)
    return do_void(txn.value('PAYMENTINFO_0_TRANSACTIONID'), note=note)
