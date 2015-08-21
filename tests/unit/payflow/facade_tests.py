from __future__ import unicode_literals
from decimal import Decimal as D
import datetime

from django.test import TestCase
from django.utils import six
from oscar.apps.payment.models import Bankcard
from oscar.apps.payment import exceptions
import mock

from paypal.payflow import facade, models, codes

"""
See page 49 of the PDF for information on PayPal's testing set-up
"""


class TestAuthorize(TestCase):

    def setUp(self):
        self.card = Bankcard(
            number='4111111111111111',
            name='John Doe',
            expiry_date=datetime.date(2015, 8, 1),
        )

    def authorize(self):
        return facade.authorize('1234', D('10.00'), self.card)

    def test_returns_approved_txn(self):
        with mock.patch('paypal.payflow.gateway.authorize') as mock_f:
            mock_f.return_value = models.PayflowTransaction(
                result='0'
            )
            txn = self.authorize()
            self.assertTrue(txn.is_approved)

    def test_raises_exception_when_not_approved(self):
        with mock.patch('paypal.payflow.gateway.authorize') as mock_f:
            mock_f.return_value = models.PayflowTransaction(
                result='1'
            )
            with self.assertRaises(exceptions.UnableToTakePayment):
                self.authorize()

    def test_not_approved_exception_contains_useful_message(self):
        with mock.patch('paypal.payflow.gateway.authorize') as mock_f:
            mock_f.return_value = models.PayflowTransaction(
                result='23',
                respmsg='Invalid account number',
            )
            try:
                self.authorize()
            except exceptions.UnableToTakePayment as e:
                self.assertEqual("Invalid account number", six.text_type(e))


class TestSale(TestCase):

    def setUp(self):
        self.card = Bankcard(
            number='4111111111111111',
            name='John Doe',
            expiry_date=datetime.date(2015, 8, 1),
        )

    def sale(self):
        return facade.sale('1234', D('10.00'), self.card)

    def test_returns_approved_transaction(self):
        with mock.patch('paypal.payflow.gateway.sale') as mock_f:
            mock_f.return_value = models.PayflowTransaction(
                result='0'
            )
            txn = self.sale()
            self.assertTrue(txn.is_approved)


class TestDelayedCapture(TestCase):

    def test_returns_nothing_when_txn_is_approved(self):
        models.PayflowTransaction.objects.create(
            trxtype=codes.AUTHORIZATION,
            comment1='1234',
            pnref='V19A3A079142',
            response_time=0,
        )
        with mock.patch('paypal.payflow.gateway.delayed_capture') as mock_f:
            mock_f.return_value = models.PayflowTransaction(
                result='0'
            )
            facade.delayed_capture('1234')
