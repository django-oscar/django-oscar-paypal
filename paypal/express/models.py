import re
from django.db import models
import urlparse


class ExpressTransaction(models.Model):

    # The PayPal method and version used
    method = models.CharField(max_length=32)
    version = models.CharField(max_length=8)

    # Transaction details used in GetExpressCheckout
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                 blank=True)
    currency = models.CharField(max_length=8, null=True, blank=True)

    # Response params
    SUCCESS, SUCCESS_WITH_WARNING, FAILURE = 'Success', 'SuccessWithWarning', 'Failure'
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
        app_label = 'paypal'

    def save(self, *args, **kwargs):
        self.raw_request = re.sub(r'PWD=\d+&', 'PWD=XXXXXX&', self.raw_request)
        return super(ExpressTransaction, self).save(*args, **kwargs)

    @property
    def is_successful(self):
        return self.ack in (self.SUCCESS, self.SUCCESS_WITH_WARNING)

    @property
    def context(self):
        return urlparse.parse_qs(self.raw_response)

    def request(self):
        request_params = urlparse.parse_qs(self.raw_request)
        return self._as_table(request_params)
    request.allow_tags = True

    def response(self):
        return self._as_table(self.context)
    response.allow_tags = True

    def _as_table(self, params):
        rows = []
        for k, v in sorted(params.items()):
            rows.append('<tr><th>%s</th><td>%s</td></tr>' % (k, v[0]))
        return '<table>%s</table>' % ''.join(rows)

    def __unicode__(self):
        return u'<Transaction method: %s: token: %s>' % (
            self.method, self.token)

    def value(self, key):
        ctx = self.context
        return ctx[key][0] if key in ctx else None
