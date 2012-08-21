from decimal import Decimal as D

from django.test import TestCase
from django.utils import unittest
from django.conf import settings

from paypal.payflow import gateway


@unittest.skipUnless(getattr(settings, 'PAYPAL_RUN_EXTERNAL_TESTS', False),
                    "External tests are not enabled")
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
        txn = gateway.authorize('1234', '4111111111111111', '123', '1213', D('12.99'),
                                **params)
        self.assertTrue(txn.is_approved)

    def test_sale_without_address_returns_successful_txn(self):
        txn = gateway.sale('1234', '4111111111111111', '123', '1213', D('12.99'))
        self.assertTrue(txn.is_approved)

    def test_auth_then_delayed_capture(self):
        params = {
            'first_name': 'Barry',
            'last_name': 'Chuckle',
            'street': '1 Road',
            'city': 'Liverpool',
            'zip': 'L1 9ET',
        }
        auth_txn = gateway.authorize('1234', '4111111111111111', '123', '1213', D('12.99'),
                                     **params)
        capture_txn = gateway.delayed_capture('1234', auth_txn.pnref)

        # Normally this fails as the auth_txn is not approved
        self.assertFalse(capture_txn.is_approved)

    def test_credit_after_sale(self):
        sale_txn = gateway.sale('1234', '4111111111111111', '123', '1213', D('12.99'))
        credit_txn = gateway.credit('1234', sale_txn.pnref)

        # Normally this fails as the auth_txn is not approved
        self.assertFalse(credit_txn.is_approved)
