from django.conf import settings
from oscar.apps.payment import exceptions

from . import gateway


def pay(ip_address):
    """
    Submit a 'Pay' request and get a redirect URL in response
    """
    # Fake receivers
    receivers = (
        gateway.Receiver(email='david._1332854868_per@gmail.com',
                         amount=D('12.00'), is_primary=True),
        gateway.Receiver(email='david._1359545821_pre@gmail.com',
                         amount=D('12.00'), is_primary=False),
    )
    txn = gateway.pay(
        recipients=recipients,
        currency=settings.PAYPAL_CURRENCY,
        return_url=return_url,
        cancel_url=cancel_url,
        ip_address=ip_address)
    if not txn.is_successful:
        raise excpeptions.UnableToTakePayment()
