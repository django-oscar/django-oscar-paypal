from unittest import TestCase

import pytest

from paypal.express.models import ExpressTransaction as Transaction


@pytest.mark.django_db
class TransactionTests(TestCase):

    def test_password_is_not_saved(self):
        payload = 'PAYMENTACTION=Sale&PAYERID=7ZTRBDFYYA47W&CURRENCYCODE=GBP&TOKEN=EC-9LW34435GU332960W&AMT=6.99&PWD=1432777837&VERSION=60.0&USER=test_1332777813_biz_api1.gmail.com&SIGNATURE=A22DCxaCv-WeMRC6ke.fAabwPrYNAH6IkVF8xxY9XZI3Qtl0q-2XLULA&METHOD=DoExpressCheckoutPayment'    # noqa E501
        txn = Transaction.objects.create(raw_request=payload,
                                         response_time=0)
        self.assertTrue('1432777837' not in txn.raw_request)

    def test_query_param_extraction(self):
        response = 'TOKEN=EC%2d8P797793UC466090M&CHECKOUTSTATUS=PaymentActionNotInitiated&TIMESTAMP=2012%2d04%2d16T11%3a51%3a57Z&CORRELATIONID=ab8a263eb440&ACK=Success&VERSION=60%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=6%2e99&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00'   # noqa E501
        txn = Transaction.objects.create(raw_request='',
                                         raw_response=response,
                                         response_time=0)
        self.assertEqual('PaymentActionNotInitiated', txn.value('CHECKOUTSTATUS'))

    def test_warnings_are_successful(self):
        txn = Transaction.objects.create(raw_request='',
                                         raw_response='',
                                         ack='SuccessWithWarning',
                                         response_time=0)
        self.assertTrue(txn.is_successful)
