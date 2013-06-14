"""
Responsible for briding between Oscar and the PayPal gateway
"""
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from paypal.express.models import ExpressTransaction as Transaction
from paypal.express.gateway import (
    set_txn, get_txn, do_txn, SALE, AUTHORIZATION, ORDER,
    do_capture, DO_EXPRESS_CHECKOUT, do_void, refund_txn
)


def _get_payment_action():
    # PayPal supports 3 actions: 'Sale', 'Authorization', 'Order'
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)
    if action not in (SALE, AUTHORIZATION, ORDER):
        raise ImproperlyConfigured("'%s' is not a valid payment action" % action)
    return action


def get_paypal_url(basket, shipping_methods, user=None, shipping_address=None,
                   shipping_method=None, host=None, scheme='https'):
    """
    Return the URL for PayPal Express transaction.

    This involves registering the txn with PayPal to get a one-time
    URL.  If a shipping method and shipping address are passed, then these are
    given to PayPal directly - this is used within when using PayPal as a
    payment method.
    """
    currency = getattr(settings, 'PAYPAL_CURRENCY', 'GBP')
    if host is None:
        host = Site.objects.get_current().domain
    return_url = '%s://%s%s' % (
        scheme, host, reverse('paypal-success-response', kwargs={
            'basket_id': basket.id}))
    cancel_url = '%s://%s%s' % (
        scheme, host, reverse('paypal-cancel-response', kwargs={
            'basket_id': basket.id}))

    # URL for updating shipping methods - we only use this if we have a set of
    # shipping methods to choose between.
    update_url = None
    if shipping_methods:
        update_url = '%s://%s%s' % (scheme, host, reverse('paypal-shipping-options',
                                                        kwargs={'basket_id': basket.id}))

    # Pass a default billing address is there is one.  This means PayPal can
    # pre-fill the registration form.
    address = None
    if user:
        addresses = user.addresses.all().order_by('-is_default_for_billing')
        if len(addresses):
            address = addresses[0]

    return set_txn(basket=basket,
                   shipping_methods=shipping_methods,
                   currency=currency,
                   return_url=return_url,
                   cancel_url=cancel_url,
                   update_url=update_url,
                   action=_get_payment_action(),
                   shipping_method=shipping_method,
                   shipping_address=shipping_address,
                   user=user,
                   user_address=address)


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
    return refund_txn(txn.value('TRANSACTIONID'), is_partial, amount, currency)


def capture_authorization(token, note=None):
    """
    Capture a previous authorization.
    """
    txn = Transaction.objects.get(token=token,
                                  method=DO_EXPRESS_CHECKOUT)
    return do_capture(txn.value('TRANSACTIONID'),
                      txn.amount, txn.currency, note=note)


def void_authorization(token, note=None):
    """
    Void a previous authorization.
    """
    txn = Transaction.objects.get(token=token,
                                  method=DO_EXPRESS_CHECKOUT)
    return do_void(txn.value('TRANSACTIONID'), note=note)
