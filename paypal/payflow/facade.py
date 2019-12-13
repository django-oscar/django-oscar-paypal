"""
Bridging module between Oscar and the gateway module (which is Oscar agnostic)
"""
from oscar.apps.payment import exceptions

from paypal.payflow import codes, gateway, models


def authorize(order_number, amt, bankcard, billing_address=None):
    """
    Make an *authorisation* request

    This holds the money on the customer's bank account but does not mark the
    transaction for settlement.  This is the most common method to use for
    fulfilling goods that require shipping.  When the goods are ready to be
    shipped, the transaction can be marked for settlement by calling the
    delayed_capture method.

    If successful, return nothing ("silence is golden") - if unsuccessful raise
    an exception which can be caught and handled within view code.

    :order_number: Order number for request
    :amt: Amount for transaction
    :bankcard: Instance of Oscar's Bankcard class (which is just a dumb wrapper
               around the pertinent bankcard attributes).
    :billing_address: A dict of billing address information (which can
                      come from the `cleaned_data` of a billing address form).
    """
    return _submit_payment_details(
        gateway.authorize, order_number, amt, bankcard, billing_address)


def sale(order_number, amt, bankcard, billing_address=None):
    """
    Make a *sale* request

    This holds the money on the customer's bank account and marks the
    transaction for settlement that night.  This is appropriate method to use
    for products that can be immediately fulfilled - such as digital products.

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


def _submit_payment_details(
        gateway_fn, order_number, amt, bankcard, billing_address=None):
    # Remap address fields if set.
    address_fields = {}
    if billing_address:
        address_fields.update({
            'first_name': billing_address['first_name'],
            'last_name': billing_address['last_name'],
            'street': billing_address['line1'],
            'city': billing_address['line4'],
            'state': billing_address['state'],
            'zip': billing_address['postcode'].strip(' ')
        })

    txn = gateway_fn(
        order_number,
        card_number=bankcard.number,
        cvv=bankcard.cvv,
        expiry_date=bankcard.expiry_month("%m%y"),
        amt=amt,
        **address_fields)
    if not txn.is_approved:
        raise exceptions.UnableToTakePayment(txn.respmsg)
    return txn


def delayed_capture(order_number, pnref=None, amt=None):
    """
    Capture funds that have been previously authorized.

    Notes:

    * It's possible to capture a lower amount than the original auth
      transaction - however...
    * ...only one delayed capture is allowed for a given PNREF...
    * ...If multiple captures are required, a 'reference transaction' needs to be
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

    This is equivalent to a *sale* transaction but without the user having to
    enter their payment details.

    There are two main uses for this:

    1. This allows customers to checkout without having to re-enter their
       payment details.

    2. It allows an initial authorisation to be settled in multiple parts.  The
       first settle should use delayed_capture but any subsequent ones should
       use this method.

    :order_number: Order number.
    :pnref: PNREF of a previous transaction to use.
    :amt: The amount to settle for.
    """
    txn = gateway.reference_transaction(
        order_number, pnref, amt)
    if not txn.is_approved:
        raise exceptions.UnableToTakePayment(txn.respmsg)
    return txn


def void(order_number, pnref):
    """
    Void an authorisation transaction to prevent it from being settled

    :order_number: Order number
    :pnref: The PNREF of the transaction to void.
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
    :amt: A custom amount to capture.  If not specified, the entire transaction
          is refuneded.
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
