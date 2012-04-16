from unittest import TestCase

from paypal.express.models import Transaction


class TransactionTests(TestCase):

    def test_password_is_not_saved(self):
        payload = 'PAYMENTACTION=Sale&PAYERID=7ZTRBDFYYA47W&CURRENCYCODE=GBP&TOKEN=EC-9LW34435GU332960W&AMT=6.99&PWD=1432777837&VERSION=60.0&USER=test_1332777813_biz_api1.gmail.com&SIGNATURE=A22DCxaCv-WeMRC6ke.fAabwPrYNAH6IkVF8xxY9XZI3Qtl0q-2XLULA&METHOD=DoExpressCheckoutPayment'
        txn = Transaction.objects.create(raw_request=payload,
                                        response_time=0)
        self.assertTrue('1432777837' not in txn.raw_request)
