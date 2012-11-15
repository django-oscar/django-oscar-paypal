from decimal import Decimal as D
from unittest import TestCase
from mock import patch, Mock

from oscar.apps.shipping.methods import Free

from paypal.express import gateway
from paypal import exceptions
from paypal.express.models import ExpressTransaction as Transaction


class MockedResponseTestCase(TestCase):

    def setUp(self):
        self.basket = self.create_mock_basket()
        self.methods = [Free()]

    def create_mock_basket(self):
        basket = Mock()
        basket.total_incl_tax = D('10.00')
        basket.all_lines = Mock(return_value=[])
        basket.get_discounts = Mock(return_value=[])
        return basket

    def tearDown(self):
        Transaction.objects.all().delete()

    def create_mock_response(self, body, status_code=200):
        response = Mock()
        response.content = body
        response.status_code = status_code
        return response


class ErrorResponseTests(MockedResponseTestCase):

    def test_error_response_raises_exception(self):
        response_body = 'TIMESTAMP=2012%2d03%2d26T16%3a33%3a09Z&CORRELATIONID=3bea2076bb9c3&ACK=Failure&VERSION=0%2e000000&BUILD=2649250&L_ERRORCODE0=10002&L_SHORTMESSAGE0=Security%20error&L_LONGMESSAGE0=Security%20header%20is%20not%20valid&L_SEVERITYCODE0=Error'
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
        response_body = 'TOKEN=EC%2d6469953681606921P&TIMESTAMP=2012%2d03%2d26T17%3a19%3a38Z&CORRELATIONID=50a8d895e928f&ACK=Success&VERSION=60%2e0&BUILD=2649250'
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
