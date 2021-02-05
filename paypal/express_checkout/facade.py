import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from paypal.express_checkout.gateway import PaymentProcessor, buyer_pays_on_paypal
from paypal.express_checkout.models import ExpressCheckoutTransaction as Transaction


def get_intent():
    intent = getattr(settings, 'PAYPAL_ORDER_INTENT', Transaction.CAPTURE)
    if intent not in (Transaction.CAPTURE, Transaction.AUTHORIZE):
        message = _("'%s' is not a valid order intent") % intent
        raise ImproperlyConfigured(message)
    return intent


def get_paypal_url(basket, user=None, shipping_address=None, shipping_method=None, host=None):
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

    use_https = getattr(settings, 'PAYPAL_CALLBACK_HTTPS', True)
    scheme = 'https' if use_https else 'http'

    view_name = 'express-checkout-handle-order' if buyer_pays_on_paypal() else 'express-checkout-success-response'
    return_url_path = reverse(view_name, kwargs={'basket_id': basket.id})
    return_url = f'{scheme}://{host}{return_url_path}'

    cancel_url_path = reverse('express-checkout-cancel-response', kwargs={'basket_id': basket.id})
    cancel_url = f'{scheme}://{host}{cancel_url_path}'

    address = None
    if basket.is_shipping_required():
        if shipping_address is not None:
            address = shipping_address
        elif user is not None:
            addresses = user.addresses.all().order_by('-is_default_for_billing')
            if addresses.exists():
                address = addresses.first()

    shipping_charge = None
    order_total = basket.total_incl_tax
    if shipping_method:
        shipping_charge = shipping_method.calculate(basket).incl_tax
        order_total += shipping_charge

    intent = get_intent()

    result = PaymentProcessor().create_order(
        basket=basket,
        currency=currency,
        return_url=return_url,
        cancel_url=cancel_url,
        order_total=order_total,
        address=address,
        shipping_charge=shipping_charge,
        intent=intent,
    )

    Transaction.objects.create(
        order_id=result.id,
        amount=order_total,
        currency=currency,
        status=result.status,
        intent=intent,
    )

    for link in result.links:
        if link.rel == 'approve':
            return link.href


def fetch_transaction_details(token):
    """
    Fetch the details about the PayPal transaction.
    """

    transaction = Transaction.objects.get(order_id=token)

    if not transaction.payer_id:
        result = PaymentProcessor().get_order(token)
        transaction.payer_id = result.payer.payer_id
        transaction.email = result.payer.email_address
        transaction.status = result.status
        try:
            transaction.address_full_name = result.purchase_units[0].shipping.name.full_name
            transaction.address = json.dumps(result.purchase_units[0].shipping.address.dict())
        except AttributeError:
            pass
        transaction.save()

    if transaction.is_authorization and not transaction.authorization_id:
        result = PaymentProcessor().authorize_order(transaction.order_id)
        transaction.authorization_id = result.purchase_units[0].payments.authorizations[0].id
        transaction.status = result.status
        transaction.save()

    return transaction


def capture_order(token):
    transaction = Transaction.objects.get(order_id=token)
    if transaction.is_authorization:
        capture_token = transaction.authorization_id
    else:
        capture_token = transaction.order_id

    result = PaymentProcessor().capture_order(capture_token, transaction.intent)
    capture_id = result.id if transaction.is_authorization else result.purchase_units[0].payments.captures[0].id
    transaction.capture_id = capture_id
    transaction.status = Transaction.COMPLETED
    transaction.save()
    return transaction


def refund_order(token):
    transaction = Transaction.objects.get(order_id=token)

    result = PaymentProcessor().refund_order(transaction.capture_id, transaction.amount, transaction.currency)

    transaction.refund_id = result.id
    transaction.save()
    return transaction


def void_authorization(token):
    """
    Void a previous authorization.
    """

    transaction = Transaction.objects.get(order_id=token)

    PaymentProcessor().void_authorized_order(transaction.authorization_id)

    transaction.status = Transaction.VOIDED
    transaction.save()
    return transaction
