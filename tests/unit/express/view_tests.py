import random
from contextlib import nested

from decimal import Decimal as D

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from mock import patch, Mock

from oscar.apps.order.models import Order
from oscar.apps.basket.models import Basket
from oscar.core.loading import get_classes

from purl import URL


Partner, StockRecord = get_classes('partner.models', ('Partner',
                                                      'StockRecord'))

(ProductClass,
 Product,
 ProductAttribute,
 ProductAttributeValue) = get_classes('catalogue.models', (
    'ProductClass', 'Product', 'ProductAttribute', 'ProductAttributeValue'))


def create_product(price=None, title=u"Dummy title",
                   product_class=u"Dummy item class", partner=u"Dummy partner",
                   partner_sku=None, upc=None, num_in_stock=10,
                   attributes=None, **kwargs):
    """
    Helper method for creating products that are used in tests.

    Ported from oscar_testsupport. Where the function is present:
        Oscar 0.4: oscar.test.helpers
        Oscar 0.5: oscar_testsupport
        Oscar 0.6: oscar.test.factories
    """
    ic, __ = ProductClass._default_manager.get_or_create(name=product_class)
    item = Product(title=title, product_class=ic, upc=upc, **kwargs)

    if attributes:
        for key, value in attributes.items():
            setattr(item.attr, key, value)

    item.save()

    if price is not None or partner_sku or num_in_stock is not None:
        if not partner_sku:
            partner_sku = 'sku_%d_%d' % (item.id, random.randint(0, 10000))
        if price is None:
            price = D('10.00')

        partner, __ = Partner._default_manager.get_or_create(name=partner)
        StockRecord._default_manager.create(product=item, partner=partner,
                                            partner_sku=partner_sku,
                                            price_excl_tax=price,
                                            num_in_stock=num_in_stock)
    return item


class MockedPayPalTests(TestCase):
    fixtures = ['countries.json']
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


class EdgeCaseTests(MockedPayPalTests):

    def setUp(self):
        self.client = Client()

    def test_empty_basket_shows_error(self):
        url = reverse('paypal-redirect')
        response = self.client.get(url)
        self.assertEqual(reverse('basket:summary'), URL.from_string(response['Location']).path())

    def test_missing_shipping_address(self):
        from paypal.express.views import RedirectView
        with patch.object(RedirectView, 'as_payment_method') as as_payment_method:
            as_payment_method.return_value = True

            url = reverse('paypal-redirect')
            self.add_product_to_basket()
            response = self.client.get(url)
            self.assertEqual(
                reverse('checkout:shipping-address'),
                URL.from_string(response['Location']).path()
            )

    def test_missing_shipping_method(self):
        from paypal.express.views import RedirectView

        with nested(
                patch.object(RedirectView, 'as_payment_method'),
                patch.object(RedirectView, 'get_shipping_address'),
                patch.object(RedirectView, 'get_shipping_method')
            ) as (as_payment_method, get_shipping_address, get_shipping_method):

            as_payment_method.return_value = True
            get_shipping_address.return_value = Mock()
            get_shipping_method.return_value = None

            url = reverse('paypal-redirect')
            self.add_product_to_basket()
            response = self.client.get(url)
            self.assertEqual(
                reverse('checkout:shipping-method'),
                URL.from_string(response['Location']).path()
            )


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
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-success-response',
                      kwargs={'basket_id': basket.id})
        url = URL().path(url)\
                   .query_param('PayerID', '12345')\
                   .query_param('token', 'EC-8P797793UC466090M')
        self.response = self.client.get(str(url), follow=True)

    def test_context(self):
        self.assertTrue('paypal_amount' not in self.response.context)


class PreviewOrderTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-success-response',
                      kwargs={'basket_id': basket.id})

        url = URL().path(url)\
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
            self.assertTrue(k in self.response.context, "%s not in context" % k)


class SubmitOrderTests(MockedPayPalTests):

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))

        # Explicitly freeze basket
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-place-order', kwargs={'basket_id': basket.id})
        self.response = self.client.post(
            url, {'action': 'place_order',
                  'payer_id': '12345',
                  'token': 'EC-8P797793UC466090M'})
        self.order = Order.objects.all()[0]

    def patch_http_post(self, post):
        get_response = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOSTREET2=line2&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOSTREET2=line2&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'
        do_response = 'TOKEN=EC%2d6WY34243AN3588740&SUCCESSPAGEREDIRECTREQUESTED=false&TIMESTAMP=2012%2d04%2d19T10%3a07%3a47Z&CORRELATIONID=3db1d5276ddfd&ACK=Success&VERSION=88%2e0&BUILD=2808426&INSURANCEOPTIONSELECTED=false&SHIPPINGOPTIONISDEFAULT=false&PAYMENTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTINFO_0_TRANSACTIONTYPE=expresscheckout&PAYMENTINFO_0_PAYMENTTYPE=instant&PAYMENTINFO_0_ORDERTIME=2012%2d04%2d19T09%3a42%3a50Z&PAYMENTINFO_0_AMT=33%2e98&PAYMENTINFO_0_FEEAMT=1%2e36&PAYMENTINFO_0_TAXAMT=0%2e00&PAYMENTINFO_0_CURRENCYCODE=GBP&PAYMENTINFO_0_PAYMENTSTATUS=Pending&PAYMENTINFO_0_PENDINGREASON=paymentreview&PAYMENTINFO_0_REASONCODE=None&PAYMENTINFO_0_PROTECTIONELIGIBILITY=Ineligible&PAYMENTINFO_0_PROTECTIONELIGIBILITYTYPE=None&PAYMENTINFO_0_SECUREMERCHANTACCOUNTID=YYH7BB4UHPKC4&PAYMENTINFO_0_ERRORCODE=0&PAYMENTINFO_0_ACK=Success'
        def side_effect(url, payload):
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

    def test_shipping_address_includes_line2(self):
        self.assertEqual('line2', self.order.shipping_address.line2)


class SubmitOrderErrorsTests(MockedPayPalTests):

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))

        # Explicitly freeze basket
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-place-order', kwargs={'basket_id': basket.id})
        self.response = self.client.post(
            url, {'action': 'place_order',
                  'payer_id': '12345',
                  'token': 'EC-8P797793UC466090M'})

    def patch_http_post(self, post):
        get_response = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOSTREET2=line2&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOSTREET2=line2&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'
        error_response = 'Error'
        def side_effect(url, payload):
            if 'GetExpressCheckoutDetails' in payload:
                return self.get_mock_response(get_response)
            elif 'DoExpressCheckoutPayment' in payload:
                return self.get_mock_response(error_response)
        post.side_effect = side_effect

    def test_paypal_error(self):
        self.assertTrue('error' in self.response.context_data)

        error = self.response.context_data['error']
        self.assertEqual(error, "A problem occurred while processing payment for this "
                      "order - no payment has been taken.  Please "
                      "contact customer services if this problem persists")
