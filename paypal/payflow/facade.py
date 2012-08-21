"""
Bridging module between Oscar and the gateway module (which is Oscar agnostic)
"""
from paypal.payflow import gateway


class NotApproved(Exception):
    pass


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

    txn = gateway.authorize(
        order_number,
        card_number=bankcard.card_number,
        cvv=bankcard.cvv,
        expiry_date=exp_date,
        amt=amt,
        **address_fields)
    if not txn.is_approved:
        raise NotApproved(txn.respmsg)


def settle():
    pass


def refund():
    pass
