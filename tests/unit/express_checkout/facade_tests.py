from decimal import Decimal as D
from unittest.mock import patch

from django.test import TestCase
from paypalhttp.http_response import construct_object

from paypal.express_checkout.facade import refund_order, void_authorization
from paypal.express_checkout.models import ExpressCheckoutTransaction

from .mocked_data import REFUND_ORDER_DATA_MINIMAL


class FacadeTests(TestCase):

    def setUp(self):
        super().setUp()

        # Before getting order must be created
        self.txn = ExpressCheckoutTransaction.objects.create(
            order_id='4MW805572N795704B',
            capture_id='45315376249711632',
            amount=D('0.99'),
            currency='GBP',
            status=ExpressCheckoutTransaction.CREATED,
            intent=ExpressCheckoutTransaction.CAPTURE,
        )

    def test_refund_order(self):
        with patch('paypal.express_checkout.facade.PaymentProcessor.refund_order') as mocked_refund_order:
            mocked_refund_order.return_value = construct_object('Result', REFUND_ORDER_DATA_MINIMAL)

            refund_order('4MW805572N795704B')

            self.txn.refresh_from_db()
            assert self.txn.refund_id == '0SM71185A67927728'

            mocked_refund_order.assert_called_once_with('45315376249711632', D('0.99'), 'GBP')

    def test_void_authorization(self):
        self.txn.authorization_id = '3PW0120338716941H'
        self.txn.save()

        with patch('paypal.express_checkout.facade.PaymentProcessor.void_authorized_order') as mocked_void_order:
            mocked_void_order.return_value = None

            void_authorization('4MW805572N795704B')

            self.txn.refresh_from_db()
            assert self.txn.status == ExpressCheckoutTransaction.VOIDED

            mocked_void_order.assert_called_once_with('3PW0120338716941H')
