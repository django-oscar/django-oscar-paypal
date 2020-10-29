import re

from django.db import models
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from paypal import base
from paypal.payflow import codes


class PayflowTransaction(base.ResponseModel):
    # This is the linking parameter between the merchant and PayPal.  It is
    # normally set to the order number
    comment1 = models.CharField(_("Comment 1"), max_length=128, db_index=True)

    trxtype = models.CharField(_("Transaction type"), max_length=12)
    tender = models.CharField(_("Bankcard or PayPal"), max_length=12, null=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                 blank=True)

    # Response params
    pnref = models.CharField(_("Payflow transaction ID"), max_length=32,
                             unique=True, null=True)
    ppref = models.CharField(_("Payment transaction ID"), max_length=32,
                             null=True)
    result = models.CharField(max_length=32, null=True, blank=True)
    respmsg = models.CharField(_("Response message"), max_length=512)
    authcode = models.CharField(_("Auth code"), max_length=32, null=True,
                                blank=True)

    # Fraud/risk params
    cvv2match = models.CharField(_("CVV2 check"), null=True, blank=True,
                                 max_length=12)
    avsaddr = models.CharField(_("House number check"), null=True, blank=True,
                               max_length=1)
    avszip = models.CharField(_("Zip/Postcode check"), null=True, blank=True, max_length=1)

    class Meta:
        ordering = ('-date_created',)
        app_label = 'paypal'

    def save(self, *args, **kwargs):
        self.raw_request = re.sub(r'PWD=.+?&', 'PWD=XXXXXX&', self.raw_request)
        self.raw_request = re.sub(r'ACCT=\d+(\d{4})&', 'ACCT=XXXXXXXXXXXX\1&', self.raw_request)
        self.raw_request = re.sub(r'CVV2=\d+&', 'CVV2=XXX&', self.raw_request)
        return super(PayflowTransaction, self).save(*args, **kwargs)

    def get_trxtype_display(self):
        return gettext(codes.trxtype_map.get(self.trxtype, self.trxtype))
    get_trxtype_display.short_description = _("Transaction type")

    def get_tender_display(self):
        return gettext(codes.tender_map.get(self.tender, ''))
    get_tender_display.short_description = _("Tender")

    @property
    def is_approved(self):
        return self.result in ('0', '126')

    def is_address_verified(self):
        return self.avsaddr == 'Y' and self.avzip == 'Y'

    def __str__(self):
        return self.pnref

    @property
    def can_be_voided(self):
        if self.trxtype != codes.AUTHORIZATION:
            return False
        return self.is_approved

    @property
    def can_be_credited(self):
        """
        Test if this txn can be credited
        """
        if self.trxtype not in (codes.SALE, codes.DELAYED_CAPTURE):
            return False
        return self.is_approved

    @property
    def can_be_captured(self):
        """
        Test if this txn can be captured
        """
        if self.trxtype != codes.AUTHORIZATION:
            return False
        return self.is_approved
