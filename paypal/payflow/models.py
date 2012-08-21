import re
import urlparse

from django.db import models
from django.utils.translation import ugettext_lazy as _

from paypal.payflow import codes


class PayflowTransaction(models.Model):
    trxtype = models.CharField(_("Transaction type"), max_length=12)
    tender = models.CharField(_("Bankcard or PayPal"), max_length=12)

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                 blank=True)

    # Response params
    pnref = models.CharField(_("Payflow transaction ID"), max_length=32)
    ppref = models.CharField(_("Payment transaction ID"), max_length=32,
                             unique=True, null=True)
    cvv2match = models.CharField(_("CVV2 check"), null=True, blank=True,
                                 max_length=12)
    result = models.CharField(max_length=32, null=True, blank=True)
    respmsg = models.CharField(_("Response message"), max_length=512)
    authcode = models.CharField(_("Auth code"), max_length=32, null=True,
                                blank=True)

    # Audit information
    raw_request = models.TextField(max_length=512)
    raw_response = models.TextField(max_length=512)
    response_time = models.FloatField(help_text="Response time in milliseconds")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def save(self, *args, **kwargs):
        self.raw_request = re.sub(r'PWD=.+&', 'PWD=XXXXXX&', self.raw_request)
        self.raw_request = re.sub(r'ACCT=\d+(\d{4})&', 'ACCT=XXXXXXXXXXXX\1&', self.raw_request)
        self.raw_request = re.sub(r'CVV2=\d+&', 'CVV2=XXX&', self.raw_request)
        return super(PayflowTransaction, self).save(*args, **kwargs)

    def get_trxtype_display(self):
        return codes.trxtype_map.get(self.trxtype, self.trxtype)
    get_trxtype_display.short_description = "Transaction type"

    def get_tender_display(self):
        return codes.tender_map.get(self.tender, '')
    get_tender_display.short_description = "Tender"

    @property
    def is_approved(self):
        return self.result in ('0', '126')

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

    def value(self, key):
        ctx = self.context
        return ctx[key][0] if key in ctx else None

    def __unicode__(self):
        return self.pnref
