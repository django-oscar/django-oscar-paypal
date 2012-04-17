from decimal import Decimal as D
from unittest import TestCase
from mock import patch, Mock
from purl import URL
from django.contrib.sites.models import Site

from paypal.express.models import Transaction
from paypal.express.facade import get_paypal_url, fetch_transaction_details


class MockedResponseTests(TestCase):
    token = ''
    response_body = ''

    def setUp(self):
        response = Mock()
        response.content = self.response_body
        response.status_code = 200
        with patch('requests.post') as post:
            post.return_value = response
            self.perform_action()

    def perform_action(self):
        pass

    def tearDown(self):
        Transaction.objects.all().delete()


class SuccessfulSetExpressCheckoutTests(MockedResponseTests):
    token = 'EC-6469953681606921P'
    response_body = 'TOKEN=EC%2d6469953681606921P&TIMESTAMP=2012%2d03%2d26T17%3a19%3a38Z&CORRELATIONID=50a8d895e928f&ACK=Success&VERSION=60%2e0&BUILD=2649250'

    def perform_action(self):
        basket = Mock()
        basket.total_incl_tax = D('200')
        basket.all_lines = Mock(return_value=[])
        url_str = get_paypal_url(basket)
        self.url = URL.from_string(url_str)

    def test_domain_in_return_url_defaults_to_current_site(self):
        return_url = self.url.query_param('RETURNURL')
        site = Site.objects.get_current()
        self.assertTrue(site.domain in return_url)


class SuccessfulGetExpressCheckoutTests(MockedResponseTests):
    token = 'EC-9LW34435GU332960W'
    response_body = 'TOKEN=EC%2d9LW34435GU332960W&CHECKOUTSTATUS=PaymentActionNotInitiated&TIMESTAMP=2012%2d04%2d13T15%3a19%3a25Z&CORRELATIONID=83bda082c24d4&ACK=Success&VERSION=60%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=6%2e99&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00'

    def perform_action(self):
        self.txn = fetch_transaction_details(self.token)

    def test_token_is_extracted(self):
        self.assertEqual(self.token, self.txn.token)

    def test_is_successful(self):
        self.assertTrue(self.txn.is_successful)

    def test_ack(self):
        self.assertEqual('Success', self.txn.ack)

    def test_amount_is_saved(self):
        self.assertEqual(D('6.99'), self.txn.amount)

    def test_currency_is_saved(self):
        self.assertEqual('GBP', self.txn.currency)

    def test_correlation_id_is_saved(self):
        self.assertEqual('83bda082c24d4', self.txn.correlation_id)

    def test_context(self):
        ctx = self.txn.context
        values = [
            ('ACK', ['Success']),
            ('LASTNAME', ['Winterbottom']),
        ]
        for k, v in values:
            self.assertEqual(v, ctx[k])
