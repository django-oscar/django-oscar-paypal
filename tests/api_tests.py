from decimal import Decimal as D
from unittest import TestCase
from mock import patch, Mock

from paypal import express
from paypal.express.models import Transaction


class MockedResponseTests(TestCase):

    def test_error_response_raises_exception(self):
        response_body = 'TIMESTAMP=2012%2d03%2d26T16%3a33%3a09Z&CORRELATIONID=3bea2076bb9c3&ACK=Failure&VERSION=0%2e000000&BUILD=2649250&L_ERRORCODE0=10002&L_SHORTMESSAGE0=Security%20error&L_LONGMESSAGE0=Security%20header%20is%20not%20valid&L_SEVERITYCODE0=Error'
        response = Mock()
        response.content = response_body
        response.status_code = 200
        with patch('requests.post') as post:
            post.return_value = response
            with self.assertRaises(express.PayPalError):
                express.set_txn(D('10.00'), 'GBP', 'http://localhost:8000/success',
                                  'http://localhost:8000/error')


class SuccessResponseTests(TestCase):

    def setUp(self):
        response_body = 'TOKEN=EC%2d6469953681606921P&TIMESTAMP=2012%2d03%2d26T17%3a19%3a38Z&CORRELATIONID=50a8d895e928f&ACK=Success&VERSION=60%2e0&BUILD=2649250'
        response = Mock()
        response.content = response_body
        response.status_code = 200
        with patch('requests.post') as post:
            post.return_value = response
            self.url = express.set_txn(D('10.00'), 'GBP', 'http://localhost:8000/success',
                                   'http://localhost:8000/error')

    def tearDown(self):
        Transaction.objects.all().delete()

    def test_success_response_returns_url(self):
        self.assertTrue(self.url.startswith('https://www.sandbox.paypal.com'))

    def test_success_response_creates_model(self):
        txn = Transaction.objects.get(correlation_id='50a8d895e928f')
        self.assertEqual(D('10.00'), txn.amount)
        self.assertEqual('GBP', txn.currency)
        self.assertEqual('Success', txn.ack)
        self.assertEqual('60.0', txn.version)
        self.assertEqual('EC-6469953681606921P', txn.token)
