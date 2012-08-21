from decimal import Decimal as D

from django.test import TestCase
from django.utils import unittest
from oscar.apps.payment.utils import Bankcard

from paypal.payflow import facade
from paypal.payflow import models


@unittest.skip("Not running integration tests")
class TestSystem(TestCase):

    def test_returns_a_txn_instance(self):
        card = Bankcard(
            card_number='4111111111111111',
            name='John Doe',
            expiry_date='12/13',
        )
        facade.authorize('1234', card, D('10.00'))

        txn = models.PayflowTransaction.objects.all()[0]
