"""
Bridging module between Oscar and the gateway module (which is Oscar agnostic)
"""
from oscar.apps.payment import exceptions

from paypal.payflow import gateway
from paypal.payflow import models
from paypal.payflow import codes


def authorize(order_number, amt, bankcard, billing_address=None):
    """
    Make an authorisation request to PayPal.

    If successful, return nothing ("silence is golden") - if unsuccessful raise
    an exception which can be caught and handled within view code.

    :order_number: Order number for request
    :amt: Amount for transaction
    :bankcard: Instance of Oscar's Bankcard class (which is just a dumb wrapper
    around the pertinent bankcard attributes).
    :billing_address: A dict of billing address information (which can come from
    the `cleaned_data` of a billing address form.
    """
    return _submit_payment_details(gateway.authorize, order_number, amt, bankcard,
                                   billing_address)


def sale(order_number, amt, bankcard, billing_address=None):
    """
    Make a sale request to PayPal.

    If successful, return nothing ("silence is golden") - if unsuccessful raise
    an exception which can be caught and handled within view code.

    :order_number: Order number for request
    :amt: Amount for transaction
    :bankcard: Instance of Oscar's Bankcard class (which is just a dumb wrapper
    around the pertinent bankcard attributes).
    :billing_address: A dict of billing address information (which can come from
    the `cleaned_data` of a billing address form.
    """
    return _submit_payment_details(gateway.sale, order_number, amt, bankcard,
                                   billing_address)


def _submit_payment_details(gateway_fn, order_number, amt, bankcard, billing_address=None):
    # Oscar's bankcard class returns dates in form '01/02' - we strip the '/' to
    # conform to PayPal's conventions.
    exp_date = bankcard.expiry_date.replace('/', '')

    # Remap address fields if set
    address_fields = {}
    if billing_address:
        address_fields.update({
            'first_name': billing_address['first_name'],
            'last_name': billing_address['first_name'],
            'street': billing_address['line1'],
            'city': billing_address['line4'],
            'state': billing_address['state'],
            'zip': billing_address['postcode'].strip(' ')
        })

    txn = gateway_fn(
        order_number,
        card_number=bankcard.card_number,
        cvv=bankcard.cvv,
        expiry_date=exp_date,
        amt=amt,
        **address_fields)
    if not txn.is_approved:
        raise exceptions.UnableToTakePayment(txn.respmsg)
    return txn


def delayed_capture(order_number, pnref=None, amt=None):
    """
    Capture funds that have been previously authorized.

    Note:
    * It's possible to capture a lower amount than the original auth
      transaction - however..
    * Only one delayed capture is allowed for a given PNREF.
    * If multiple captures are required, a 'reference transaction' needs to be
      used.
    * It's safe to retry captures if the first one fails or errors

    :order_number: Order number
    :pnref: The PNREF of the authorization transaction to use.  If not
    specified, the order number is used to retrieve the appropriate transaction.
    :amt: A custom amount to capture.
    """
    if pnref is None:
        # No PNREF specified, look-up the auth transaction for this order number
        # to get the PNREF from there.
        try:
            auth_txn = models.PayflowTransaction.objects.get(
                comment1=order_number, trxtype=codes.AUTHORIZATION)
        except models.PayflowTransaction.DoesNotExist:
            raise exceptions.UnableToTakePayment(
                "No authorization transaction found with PNREF=%s" % pnref)
        pnref = auth_txn

    txn = gateway.delayed_capture(order_number, pnref, amt)
    if not txn.is_approved:
        raise exceptions.UnableToTakePayment(txn.respmsg)
    return txn


def referenced_sale(order_number, pnref, amt):
    """
    Capture funds using the bank/address details of a previous transaction
    """
    txn = gateway.reference_transaction(order_number,
                                        pnref,
                                        amt)
    if not txn.is_approved:
        raise exceptions.UnableToTakePayment(txn.respmsg)
    return txn


def void(order_number, pnref):
    """
    Void an auth transaction to prevent it from being settled
    """
    txn = gateway.void(order_number, pnref)
    if not txn.is_approved:
        raise exceptions.PaymentError(txn.respmsg)
    return txn


def credit(order_number, pnref=None, amt=None):
    """
    Return funds that have been previously settled.

    :order_number: Order number
    :pnref: The PNREF of the authorization transaction to use.  If not
    specified, the order number is used to retrieve the appropriate transaction.
    :amt: A custom amount to capture.
    """
    if pnref is None:
        # No PNREF specified, look-up the auth/sale transaction for this order number
        # to get the PNREF from there.
        try:
            auth_txn = models.PayflowTransaction.objects.get(
                comment1=order_number, trxtype__in=(codes.AUTHORIZATION,
                                                    codes.SALE))
        except models.PayflowTransaction.DoesNotExist:
            raise exceptions.UnableToTakePayment(
                "No authorization transaction found with PNREF=%s" % pnref)
        pnref = auth_txn

    txn = gateway.credit(order_number, pnref, amt)
    if not txn.is_approved:
        raise exceptions.PaymentError(txn.respmsg)
    return txn
