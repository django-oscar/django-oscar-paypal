from decimal import Decimal as D
from unittest import mock

from django.test import TestCase

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
                order_number='1234',
                card_number='4111111111111111',
                cvv='123',
                expiry_date='1214',
                amt=D('10.00'))
        self.assertTrue(txn.is_approved)

    def test_hides_card_details(self):
        with mock.patch('paypal.gateway.post') as mock_post:
            mock_post.return_value = {
                'RESULT': '126',
                'PNREF': 'V25A2BB645A7',
                'RESPMSG': 'Under review by Fraud Service',
                'AUTHCODE': '525PNI',
                'POSTFPSMSG': 'Review',
                '_raw_request': (
                    'VENDOR=oscarpaypal&TRXTYPE=A&ZIP=n12+9et&LASTNAME=&COMMENT1=100010&EXPDATE=0113'
                    '&COMMENT2=&STATE=&STREET=Flat+1+Caxton+Court&USER=oscarpaypal&CVV2=123&TENDER=C'
                    '&ACCT=5555555555554444&CITY=&FIRSTNAME=&PWD=secret&AMT=6.99'),
                '_raw_response': '',
                '_response_time': 1000
            }
            txn = gateway.authorize(
                order_number='1234',
                card_number='5555555555554444',
                cvv='123',
                expiry_date='0113',
                amt=D('6.99'))

        self.assertTrue('5555555555554444' not in txn.raw_request)
        self.assertTrue('123' not in txn.raw_request)

    def test_error_handled_gracefully(self):
        with mock.patch('paypal.gateway.post') as mock_post:
            mock_post.return_value = {
                'RESULT': '4',
                'RESPMSG': 'Invalid amount',
                '_raw_request': '',
                '_raw_response': 'RESULT=4&RESPMSG=Invalid amount',
                '_response_time': 1000
            }
            gateway.authorize(
                order_number='1234',
                card_number='5555555555554444',
                cvv='123',
                expiry_date='0113',
                amt=D('10.8000'))


class TestReferenceTransaction(TestCase):

    def test_for_smoke(self):
        with mock.patch('paypal.gateway.post') as mock_post:
            mock_post.return_value = {
                'RESULT': '1',
                'RESPMSG': '',
                '_raw_request': '',
                '_raw_response': '',
                '_response_time': 1000
            }
            gateway.reference_transaction(order_number='12345',
                                          pnref='111222',
                                          amt=D('12.23'))
