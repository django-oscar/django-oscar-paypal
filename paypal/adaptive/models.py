from django.db import models

from paypal import base


class AdaptiveTransaction(base.ResponseModel):

    # Request info
    is_sandbox = models.BooleanField(default=True)
    action = models.CharField(max_length=32)
    currency = models.CharField(max_length=32)

    # Response info
    ack = models.CharField(max_length=32)
    correlation_id = models.CharField(max_length=32, null=True, blank=True)

    # Only set if the transaction is successful.
    pay_key = models.CharField(max_length=64, null=True, blank=True)

    error_id = models.CharField(max_length=32, null=True, blank=True)
    error_message = models.CharField(max_length=256, null=True, blank=True)

    @property
    def is_successful(self):
        return self.ack == 'Success'

    @property
    def redirect_url(self):
        if self.is_sandbox:
            url = 'https://www.sandbox.paypal.com/webscr?cmd=_ap-payment&paykey=%s'
        else:
            url = 'https://www.paypal.com/webscr?cmd=_ap-payment&paykey=%s'
        return url % self.pay_key
