from django.db import models
import urlparse
import urllib


class Transaction(models.Model):

    # The PayPal method and version used
    method = models.CharField(max_length=32)
    version = models.CharField(max_length=8)

    # Transaction details used in GetExpressCheckout
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                 blank=True)
    currency = models.CharField(max_length=8, null=True, blank=True)

    # Response params
    SUCCESS, FAILURE = 'Success', 'Failure'
    ack = models.CharField(max_length=32)

    correlation_id = models.CharField(max_length=32, null=True, blank=True)
    token = models.CharField(max_length=32, null=True, blank=True)

    error_code = models.CharField(max_length=32, null=True, blank=True)
    error_message = models.CharField(max_length=256, null=True, blank=True)

    # Debug information
    raw_request = models.TextField(max_length=512)
    raw_response = models.TextField(max_length=512)

    response_time = models.FloatField(help_text="Response time in milliseconds")

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def save(self, *args, **kwargs):
        params = urlparse.parse_qs(self.raw_request)
        params['PWD'] = 'XXXXXXX'
        self.raw_request = urllib.urlencode(params)
        return super(Transaction, self).save(*args, **kwargs)

    @property
    def is_successful(self):
        return self.ack == self.SUCCESS

    @property
    def context(self):
        return urlparse.parse_qs(self.raw_response)

    def __unicode__(self):
        return u'<Transaction method: %s: token: %s>' % (
            self.method, self.token)

    def value(self, key):
        ctx = self.context
        return ctx[key][0] if key in ctx else None
