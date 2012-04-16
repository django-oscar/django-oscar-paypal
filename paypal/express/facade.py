from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from oscar.apps.payment.exceptions import PaymentError

from paypal.express import set, get, do, SET_EXPRESS_CHECKOUT
from paypal.express.models import Transaction


def get_paypal_url(basket, host=None, scheme='https'):
    """
    Return the URL for PayPal Express transaction.

    This involves registering the txn with PayPal to get a one-time
    URL.
    """
    currency = getattr(settings, 'PAYPAL_CURRENCY', 'GBP')
    if host is None:
        host = Site.objects.get_current().domain
    return_url = '%s://%s%s' % (scheme, host, reverse('paypal-success-response'))
    cancel_url = '%s://%s%s' % (scheme, host, reverse('paypal-cancel-response'))
    return set(amount=basket.total_incl_tax,
               currency=currency,
               return_url=return_url,
               cancel_url=cancel_url)


def fetch_transaction_details(token):
    return get(token)


def complete(payer_id, token, amount=None, currency=None):
    if amount is None or currency is None:
        try:
            txn = Transaction.objects.get(token=token, method=SET_EXPRESS_CHECKOUT)
        except Transaction.DoesNotExist:
            raise PaymentError("Unable to find SetExpressCheckout transaction for token %s" % token)
        amount = txn.amount
        currency = txn.currency
    return do(payer_id, token, amount, currency)

