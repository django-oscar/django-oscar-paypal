from decimal import Decimal as D

from django.test import TestCase

from paypal.payflow import gateway


class TestGateway(TestCase):

    def test_authorisation_without_address_returns_successful_txn(self):
        txn = gateway.authorize('4111111111111111', '123', '1213', D('12.99'))
        self.assertTrue(txn.is_approved)

    def test_authorisation_with_address_returns_successful_txn(self):
        params = {
            'first_name': 'Barry',
            'last_name': 'Chuckle',
            'street': '1 Road',
            'city': 'Liverpool',
            'zip': 'L1 9ET',
        }
        txn = gateway.authorize('4111111111111111', '123', '1213', D('12.99'),
                                **params)
        self.assertTrue(txn.is_approved)

    def test_sale_without_address_returns_successful_txn(self):
        txn = gateway.sale('4111111111111111', '123', '1213', D('12.99'))
        self.assertTrue(txn.is_approved)
