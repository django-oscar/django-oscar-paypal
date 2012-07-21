from paypal.payflow import gateway

class NotApproved(Exception):
    pass


def authorize(order_number, bankcard, amt):
    """
    Make an authorisation request to PayPal.  If successful, return nothing - if
    unsuccessful raise an exception.
    """
    # Oscar returns dates in form '01/02' - we strip the '/' to conform to
    # PayPal's conventions.
    exp_date = bankcard.expiry_date.replace('/', '')
    txn = gateway.authorize(
        card_number=bankcard.card_number,
        cvv=bankcard.cvv,
        expiry_date=exp_date,
        amt=amt,
        comment1=order_number)
    if not txn.is_approved:
        raise NotApproved(txn.respmsg)
