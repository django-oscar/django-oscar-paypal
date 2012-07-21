from django.test import TestCase

from paypal.payflow.models import PayflowTransaction


class TestTransactionModel(TestCase):

    def test_is_successful(self):
        txn = PayflowTransaction(
            result='0'
        )
        self.assertTrue(txn.is_approved)

    def test_fraud_referrral_is_successful(self):
        txn = PayflowTransaction(
            result='126'
        )
        self.assertTrue(txn.is_approved)
