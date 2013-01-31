from decimal import Decimal as D

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from mock import patch, Mock

from oscar.test.helpers import create_product
from oscar.apps.order.models import Order

from purl import URL


class EdgeCaseTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_empty_basket_shows_error(self):
        url = reverse('paypal-redirect')
        response = self.client.get(url)
        self.assertEqual(reverse('basket:summary'), URL.from_string(response['Location']).path())


class MockedPayPalTests(TestCase):
    response_body = None

    def setUp(self):
        self.client = Client()
        with patch('requests.post') as post:
            self.patch_http_post(post)
            self.perform_action()

    def patch_http_post(self, post):
        post.return_value = self.get_mock_response()

    def get_mock_response(self, content=None):
        response = Mock()
        response.content = self.response_body if content is None else content
        response.status_code = 200
        return response

    def perform_action(self):
        pass

    def add_product_to_basket(self, price=D('100.00')):
        product = create_product(price=price)
        self.client.post(reverse('basket:add'),
                                 {'product_id': product.id,
                                  'quantity': 1})


class RedirectToPayPalTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d8P797793UC466090M&TIMESTAMP=2012%2d04%2d16T11%3a50%3a38Z&CORRELATIONID=bdd6641577803&ACK=Success&VERSION=60%2e0&BUILD=2808426'

    def perform_action(self):
        self.add_product_to_basket()
        response = self.client.get(reverse('paypal-redirect'))
        self.url = URL.from_string(response['Location'])

    def test_nonempty_basket_redirects_to_paypal(self):
        self.assertEqual('www.sandbox.paypal.com', self.url.host())

    def test_query_params_present(self):
        params = ['cmd', 'token']
        self.assertTrue(self.url.has_query_params(params))


class FailedTxnTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d8P797793UC466090M&CHECKOUTSTATUS=PaymentActionNotInitiated&TIMESTAMP=2012%2d04%2d16T11%3a51%3a57Z&CORRELATIONID=ab8a263eb440&ACK=Failed&VERSION=60%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=6%2e99&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00'

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        url = URL().path(reverse('paypal-success-response'))\
                   .query_param('PayerID', '12345')\
                   .query_param('token', 'EC-8P797793UC466090M')
        self.response = self.client.get(str(url), follow=True)

    def test_context(self):
        self.assertTrue('paypal_amount' not in self.response.context)


class PreviewOrderTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        url = URL().path(reverse('paypal-success-response'))\
                   .query_param('PayerID', '12345')\
                   .query_param('token', 'EC-8P797793UC466090M')
        self.response = self.client.get(str(url), follow=True)

    def test_context(self):
        self.assertEqual(D('33.98'), self.response.context['paypal_amount'])

    def test_keys_in_context(self):
        keys = ('shipping_address', 'shipping_method',
                'payer_id', 'token', 'paypal_user_email',
                'paypal_amount')
        for k in keys:
            self.assertTrue(k in self.response.context)


class SubmitOrderTests(MockedPayPalTests):
    fixtures = ['countries.json']

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        self.response = self.client.post(reverse('paypal-place-order'),
                                         {'action': 'place_order',
                                          'payer_id': '12345',
                                          'token': 'EC-8P797793UC466090M'})
        self.order = Order.objects.all()[0]

    def patch_http_post(self, post):
        get_response = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'
        do_response = 'TOKEN=EC%2d6WY34243AN3588740&SUCCESSPAGEREDIRECTREQUESTED=false&TIMESTAMP=2012%2d04%2d19T10%3a07%3a47Z&CORRELATIONID=3db1d5276ddfd&ACK=Success&VERSION=88%2e0&BUILD=2808426&INSURANCEOPTIONSELECTED=false&SHIPPINGOPTIONISDEFAULT=false&PAYMENTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTINFO_0_TRANSACTIONTYPE=expresscheckout&PAYMENTINFO_0_PAYMENTTYPE=instant&PAYMENTINFO_0_ORDERTIME=2012%2d04%2d19T09%3a42%3a50Z&PAYMENTINFO_0_AMT=33%2e98&PAYMENTINFO_0_FEEAMT=1%2e36&PAYMENTINFO_0_TAXAMT=0%2e00&PAYMENTINFO_0_CURRENCYCODE=GBP&PAYMENTINFO_0_PAYMENTSTATUS=Pending&PAYMENTINFO_0_PENDINGREASON=paymentreview&PAYMENTINFO_0_REASONCODE=None&PAYMENTINFO_0_PROTECTIONELIGIBILITY=Ineligible&PAYMENTINFO_0_PROTECTIONELIGIBILITYTYPE=None&PAYMENTINFO_0_SECUREMERCHANTACCOUNTID=YYH7BB4UHPKC4&PAYMENTINFO_0_ERRORCODE=0&PAYMENTINFO_0_ACK=Success'
        def side_effect(url, payload, **kwargs):
            if 'GetExpressCheckoutDetails' in payload:
                return self.get_mock_response(get_response)
            elif 'DoExpressCheckoutPayment' in payload:
                return self.get_mock_response(do_response)
        post.side_effect = side_effect

    def test_order_total(self):
        self.assertEqual(D('6.99'), self.order.total_incl_tax)

    def test_order_email_address(self):
        self.assertEqual('david._1332854868_per@gmail.com',
                         self.order.guest_email)
