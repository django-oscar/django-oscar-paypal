from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from paypal.express import set_txn, get_txn, do_txn, PayPalError, SALE


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

    # PayPal have an upper limit on transactions.  It's in dollars which is 
    # a fiddly to work with.  Lazy solution - only check when dollars are used as
    # the PayPal currency.
    amount = basket.total_incl_tax
    if currency == 'USD' and amount > 10000:
        raise PayPalError('PayPal can only be used for orders up to 10000 USD')

    # PayPal supports 3 actions: 'Sale', 'Authorization', 'Order'
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)

    return set_txn(amount=amount,
                   currency=currency,
                   return_url=return_url,
                   cancel_url=cancel_url,
                   action=action,)


def fetch_transaction_details(token):
    """
    Fetch the completed details about the PayPal transaction.
    """
    return get_txn(token)


def complete(payer_id, token, amount, currency):
    """
    Confirm the payment action.
    """
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)
    return do_txn(payer_id, token, amount, currency, action=action)

