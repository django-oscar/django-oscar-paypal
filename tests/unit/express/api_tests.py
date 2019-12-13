from decimal import Decimal as D
from unittest.mock import Mock, patch

from django.test import TestCase
from oscar.apps.shipping.methods import FixedPrice, Free

from paypal import exceptions
from paypal.express import gateway
from paypal.express.exceptions import InvalidBasket
from paypal.express.models import ExpressTransaction as Transaction


def create_mock_basket(amt=D('10.00')):
    basket = Mock()
    basket.total_incl_tax = amt
    basket.all_lines = Mock(return_value=[])
    basket.offer_discounts = []
    basket.voucher_discounts = []
    basket.shipping_discounts = []
    return basket


class MockedResponseTestCase(TestCase):

    def setUp(self):
        self.basket = create_mock_basket()
        self.methods = [Free()]

    def tearDown(self):
        Transaction.objects.all().delete()

    def create_mock_response(self, body, status_code=200):
        response = Mock()
        response.text = body
        response.status_code = status_code
        return response


class ErrorResponseTests(MockedResponseTestCase):

    def test_error_response_raises_exception(self):
        response_body = (
            'TIMESTAMP=2012%2d03%2d26T16%3a33%3a09Z&CORRELATIONID=3bea2076bb9c3&ACK=Failure&VERSION=0%2e000000'
            '&BUILD=2649250&L_ERRORCODE0=10002&L_SHORTMESSAGE0=Security%20error'
            '&L_LONGMESSAGE0=Security%20header%20is%20not%20valid&L_SEVERITYCODE0=Error')
        response = self.create_mock_response(response_body)

        with patch('requests.post') as post:
            post.return_value = response
            with self.assertRaises(exceptions.PayPalError):
                gateway.set_txn(self.basket, self.methods, 'GBP', 'http://localhost:8000/success',
                                'http://localhost:8000/error')

    def test_non_200_response_raises_exception(self):
        response = self.create_mock_response(body='', status_code=500)

        with patch('requests.post') as post:
            post.return_value = response
            with self.assertRaises(exceptions.PayPalError):
                gateway.set_txn(self.basket, self.methods, 'GBP', 'http://localhost:8000/success',
                                'http://localhost:8000/error')


class SuccessResponseTests(MockedResponseTestCase):

    def setUp(self):
        super(SuccessResponseTests, self).setUp()
        response_body = (
            'TOKEN=EC%2d6469953681606921P&TIMESTAMP=2012%2d03%2d26T17%3a19%3a38Z&CORRELATIONID=50a8d895e928f'
            '&ACK=Success&VERSION=60%2e0&BUILD=2649250')
        response = self.create_mock_response(response_body)

        with patch('requests.post') as post:
            post.return_value = response
            self.url = gateway.set_txn(self.basket, self.methods, 'GBP',
                                       'http://localhost:8000/success',
                                       'http://localhost:8000/error')

    def test_success_response_returns_url(self):
        self.assertTrue(self.url.startswith('https://www.sandbox.paypal.com'))

    def test_success_response_creates_model(self):
        txn = Transaction.objects.get(correlation_id='50a8d895e928f')
        self.assertEqual(D('10.00'), txn.amount)
        self.assertEqual('GBP', txn.currency)
        self.assertEqual('Success', txn.ack)
        self.assertEqual('EC-6469953681606921P', txn.token)


class TestOrderTotal(TestCase):

    def test_includes_default_shipping_charge(self):
        basket = create_mock_basket(D('10.00'))
        shipping_methods = [FixedPrice(D('2.50'), D('2.50'))]

        with patch('paypal.express.gateway._fetch_response') as mock_fetch:
            gateway.set_txn(basket, shipping_methods, 'GBP', 'http://example.com',
                            'http://example.com')
            args, __ = mock_fetch.call_args

        params = args[1]
        self.assertEqual(params['PAYMENTREQUEST_0_AMT'],
                         D('10.00') + D('2.50'))

    def test_forbids_zero_value_basket(self):
        basket = create_mock_basket(D('0.00'))
        shipping_methods = [FixedPrice(D('2.50'))]

        with patch('paypal.express.gateway._fetch_response') as mock_fetch: # noqa F841
            with self.assertRaises(InvalidBasket):
                gateway.set_txn(basket, shipping_methods, 'GBP',
                                'http://example.com', 'http://example.com')
