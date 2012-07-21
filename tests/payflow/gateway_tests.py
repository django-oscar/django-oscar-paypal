from decimal import Decimal as D

from django.test import TestCase
import mock

from paypal.payflow import gateway


class TestAuthorizeFunction(TestCase):

    def test_returns_a_txn_instance(self):
        with mock.patch('paypal.gateway.post') as mock_post:
            mock_post.return_value = {
                'RESULT': '126',
                'PNREF': 'V25A2BB645A7',
                'RESPMSG': 'Under review by Fraud Service',
                'AUTHCODE': '525PNI',
                'POSTFPSMSG': 'Review',
                '_raw_request': '',
                '_raw_response': '',
                '_response_time': 1000
            }
            txn = gateway.authorize(
                card_number='4111111111111111',
                cvv='123',
                expiry_date='1214',
                amt=D('10.00'))
        self.assertTrue(txn.is_approved)
