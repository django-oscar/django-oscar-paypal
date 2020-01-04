# -*- coding: utf-8 -*-
from decimal import Decimal as D
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from django.utils.encoding import force_text
from oscar.apps.basket.models import Basket
from oscar.apps.order.models import Order
from oscar.core.loading import get_classes
from oscar.test.factories import create_product
from purl import URL

Partner, StockRecord = get_classes('partner.models', ('Partner',
                                                      'StockRecord'))

(ProductClass,
 Product,
 ProductAttribute,
 ProductAttributeValue) = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductAttribute', 'ProductAttributeValue')
)


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
        response.text = self.response_body if content is None else content
        response.status_code = 200
        return response

    def perform_action(self):
        pass

    def add_product_to_basket(self, price=D('100.00')):
        product = create_product(price=price, num_in_stock=1)
        url = reverse('basket:add', kwargs={'pk': product.pk})
        self.client.post(url, {'quantity': 1})


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

        with patch.object(RedirectView, 'as_payment_method') as as_payment_method:
            with patch.object(RedirectView, 'get_shipping_address') as get_shipping_address:
                with patch.object(RedirectView, 'get_shipping_method') as get_shipping_method:

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


class RedirectToPayPalBase(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d8P797793UC466090M&TIMESTAMP=2012%2d04%2d16T11%3a50%3a38Z&CORRELATIONID=bdd6641577803' \
                    '&ACK=Success&VERSION=60%2e0&BUILD=2808426'  # noqa E501

    def perform_action(self):
        self.add_product_to_basket()
        response = self.client.get(reverse('paypal-redirect'))
        self.url = URL.from_string(response['Location'])


class RedirectToPayPalTests(RedirectToPayPalBase):

    def test_nonempty_basket_redirects_to_paypal(self):
        self.assertEqual('www.sandbox.paypal.com', self.url.host())

    def test_query_params_present(self):
        params = ['cmd', 'token']
        self.assertTrue(self.url.has_query_params(params))


@override_settings(PAYPAL_BUYER_PAYS_ON_PAYPAL=True)
class RedirectWhenBuyerPaysOnPayPalTests(RedirectToPayPalBase):

    def test_nonempty_basket_redirects_to_paypal(self):
        self.assertEqual('www.sandbox.paypal.com', self.url.host())

    def test_query_params_present(self):
        params = ['cmd', 'token', 'useraction']
        self.assertTrue(self.url.has_query_params(params))


class FailedTxnTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d8P797793UC466090M&CHECKOUTSTATUS=PaymentActionNotInitiated' \
                    '&TIMESTAMP=2012%2d04%2d16T11%3a51%3a57Z&CORRELATIONID=ab8a263eb440&ACK=Failed' \
                    '&VERSION=60%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom' \
                    '&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom' \
                    '&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace' \
                    '&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ' \
                    '&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed' \
                    '&CURRENCYCODE=GBP&AMT=6%2e99&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00' \
                    '&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00'   # noqa E501

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-success-response', kwargs={'basket_id': basket.id})
        url = URL().path(url)\
                   .query_param('PayerID', '12345')\
                   .query_param('token', 'EC-8P797793UC466090M')
        self.response = self.client.get(str(url), follow=True)

    def test_context(self):
        self.assertTrue('paypal_amount' not in self.response.context)


class PreviewOrderTests(MockedPayPalTests):
    response_body = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted' \
                    '&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0' \
                    '&ACK=Success&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom' \
                    '&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom' \
                    '&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace' \
                    '&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ' \
                    '&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed' \
                    '&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00' \
                    '&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP' \
                    '&PAYMENTREQUEST_0_AMT=33%2e98&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00' \
                    '&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&PAYMENTREQUEST_0_TAXAMT=0%2e00' \
                    '&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00' \
                    '&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N' \
                    '&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom' \
                    '&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton' \
                    '&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ' \
                    '&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom' \
                    '&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0' \
                    '&SHIPPINGOPTIONNAME=Royal%20Mail%20Signed%20For%e2%84%a2%202nd%20Class'     # noqa E501

    def perform_action(self):
        self.add_product_to_basket(price=D('6.99'))
        basket = Basket.objects.all()[0]
        basket.freeze()
        url = reverse('paypal-success-response', kwargs={'basket_id': basket.id})

        url = URL().path(url)\
                   .query_param('PayerID', '12345')\
                   .query_param('token', 'EC-8P797793UC466090M')
        self.response = self.client.get(str(url), follow=True)

    def test_context(self):
        self.assertEqual(D('33.98'), self.response.context['paypal_amount'])
        self.assertEqual('Royal Mail Signed For™ 2nd Class',
                         force_text(self.response.context['shipping_method'].name))
        self.assertEqual('uk_rm_2ndrecorded',
                         force_text(self.response.context['shipping_method'].code))

    def test_keys_in_context(self):
        keys = ('shipping_address', 'shipping_method',
                'payer_id', 'token', 'paypal_user_email',
                'paypal_amount')
        for k in keys:
            self.assertTrue(k in self.response.context, "%s not in context" % k)


class SubmitOrderBase(MockedPayPalTests):
    get_response = ''
    do_response = ''

    def patch_http_post(self, post):
        get_response = self.get_response
        do_response = self.do_response

        def side_effect(url, payload, **kwargs):
            if 'GetExpressCheckoutDetails' in payload:
                return self.get_mock_response(get_response)
            elif 'DoExpressCheckoutPayment' in payload:
                return self.get_mock_response(do_response)
        post.side_effect = side_effect


class SubmitOrderTests(SubmitOrderBase):
    get_response = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted&' \
                   'TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success&' \
                   'VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom&' \
                   'PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom&COUNTRYCODE=GB&' \
                   'SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace&SHIPTOSTREET2=line2&' \
                   'SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&' \
                   'SHIPTOCOUNTRYNAME=United%20Kingdom&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&' \
                   'AMT=33%2e98&SHIPPINGAMT=0%2e00&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&' \
                   'SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98&' \
                   'PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&' \
                   'PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&' \
                   'PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N&' \
                   'PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom&' \
                   'PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOSTREET2=line2&' \
                   'PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands&' \
                   'PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&' \
                   'PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&' \
                   'PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTREQUESTINFO_0_ERRORCODE=0'
    do_response = 'TOKEN=EC%2d6WY34243AN3588740&SUCCESSPAGEREDIRECTREQUESTED=false&' \
                  'TIMESTAMP=2012%2d04%2d19T10%3a07%3a47Z&CORRELATIONID=3db1d5276ddfd&ACK=Success&VERSION=88%2e0&' \
                  'BUILD=2808426&INSURANCEOPTIONSELECTED=false&SHIPPINGOPTIONISDEFAULT=false&' \
                  'PAYMENTINFO_0_TRANSACTIONID=51963679RW630412N&PAYMENTINFO_0_TRANSACTIONTYPE=expresscheckout&' \
                  'PAYMENTINFO_0_PAYMENTTYPE=instant&PAYMENTINFO_0_ORDERTIME=2012%2d04%2d19T09%3a42%3a50Z&' \
                  'PAYMENTINFO_0_AMT=33%2e98&PAYMENTINFO_0_FEEAMT=1%2e36&PAYMENTINFO_0_TAXAMT=0%2e00&' \
                  'PAYMENTINFO_0_CURRENCYCODE=GBP&PAYMENTINFO_0_PAYMENTSTATUS=Pending&' \
                  'PAYMENTINFO_0_PENDINGREASON=paymentreview&PAYMENTINFO_0_REASONCODE=None&' \
                  'PAYMENTINFO_0_PROTECTIONELIGIBILITY=Ineligible&PAYMENTINFO_0_PROTECTIONELIGIBILITYTYPE=None&' \
                  'PAYMENTINFO_0_SECUREMERCHANTACCOUNTID=YYH7BB4UHPKC4&PAYMENTINFO_0_ERRORCODE=0&' \
                  'PAYMENTINFO_0_ACK=Success'

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

    def test_order_total(self):
        self.assertEqual(D('6.99'), self.order.total_incl_tax)

    def test_order_email_address(self):
        self.assertEqual('david._1332854868_per@gmail.com',
                         self.order.guest_email)

    def test_shipping_address_includes_line2(self):
        self.assertEqual('line2', self.order.shipping_address.line2)


@override_settings(PAYPAL_BUYER_PAYS_ON_PAYPAL=True)
class BuyerPaysOnPaypalResponseTests(SubmitOrderBase):
    get_response = 'TOKEN=EC%2d7F151994RW7618524&BILLINGAGREEMENTACCEPTEDSTATUS=0&' \
                   'CHECKOUTSTATUS=PaymentActionNotInitiated&' \
                   'TIMESTAMP=2014%2d12%2d14T10%3a49%3a10Z&CORRELATIONID=5ef454cceaf17&ACK=Success&VERSION=119&' \
                   'BUILD=14107150&EMAIL=info%2dbuyer%40test%2ecom&PAYERID=Y8K3PSJYN24D4&PAYERSTATUS=verified&' \
                   'FIRSTNAME=Test&LASTNAME=Buyer&COUNTRYCODE=IT&SHIPTONAME=Test%20Buyer&' \
                   'SHIPTOSTREET=street%20Test%2c%201&SHIPTOSTREET2=line2&SHIPTOCITY=London&SHIPTOSTATE=London&' \
                   'SHIPTOZIP=SW74TU&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom&' \
                   'ADDRESSSTATUS=Confirmed&CURRENCYCODE=EUR&AMT=23%2e99&ITEMAMT=23%2e99&SHIPPINGAMT=0%2e00&' \
                   'HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00&' \
                   'L_NAME0=Hacking%20Exposed%20Wireless&L_NUMBER0=9780072262582&L_QTY0=1&' \
                   'L_TAXAMT0=0%2e00&L_AMT0=23%2e99&L_DESC0=This%20is%20an%20invaluable%20resource%20for%20any%' \
                   '20IT%20professional%20who%20works%' \
                   '20with%20%2e%2e%2e&L_ITEMWEIGHTVALUE0=%20%20%200%2e00000&L_ITEMLENGTHVALUE0=%20%20%200%2e00000&' \
                   'L_ITEMWIDTHVALUE0=%20%20%200%2e00000&L_ITEMHEIGHTVALUE0=%20%20%200%2e00000&' \
                   'PAYMENTREQUEST_0_CURRENCYCODE=EUR&PAYMENTREQUEST_0_AMT=23%2e99&PAYMENTREQUEST_0_ITEMAMT=23%2e99&' \
                   'PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00&' \
                   'PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00&' \
                   'PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false&' \
                   'PAYMENTREQUEST_0_SHIPTONAME=Test%20Buyer&PAYMENTREQUEST_0_SHIPTOSTREET=street%20Test%2c%201&' \
                   'PAYMENTREQUEST_0_SHIPTOSTREET2=line2&PAYMENTREQUEST_0_SHIPTOCITY=London&' \
                   'PAYMENTREQUEST_0_SHIPTOSTATE=London&PAYMENTREQUEST_0_SHIPTOZIP=SW74TU&' \
                   'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom&' \
                   'PAYMENTREQUEST_0_ADDRESSSTATUS=Confirmed&PAYMENTREQUEST_0_ADDRESSNORMALIZATIONSTATUS=None&' \
                   'L_PAYMENTREQUEST_0_NAME0=Hacking%20Exposed%20Wireless&L_PAYMENTREQUEST_0_NUMBER0=9780072262582&' \
                   'L_PAYMENTREQUEST_0_QTY0=1&L_PAYMENTREQUEST_0_TAXAMT0=0%2e00&L_PAYMENTREQUEST_0_AMT0=23%2e99&' \
                   'L_PAYMENTREQUEST_0_DESC0=This%20is%20an%20invaluable%20resource%20for%20any%20IT%20professional' \
                   '%20who%20works%20with%20%2e%2e%2e&L_PAYMENTREQUEST_0_ITEMWEIGHTVALUE0=%20%20%200%2e00000&' \
                   'L_PAYMENTREQUEST_0_ITEMLENGTHVALUE0=%20%20%200%2e00000&' \
                   'L_PAYMENTREQUEST_0_ITEMWIDTHVALUE0=%20%20%200%2e00000&' \
                   'L_PAYMENTREQUEST_0_ITEMHEIGHTVALUE0=%20%20%200%2e00000&PAYMENTREQUESTINFO_0_ERRORCODE=0'
    do_response = 'TOKEN=EC%2d7F151994RW7618524&SUCCESSPAGEREDIRECTREQUESTED=false&' \
                  'TIMESTAMP=2014%2d12%2d14T10%3a49%3a42Z&CORRELATIONID=30e7eb7f96acc&ACK=Success&VERSION=119&' \
                  'BUILD=14107150&INSURANCEOPTIONSELECTED=false&SHIPPINGOPTIONISDEFAULT=false&' \
                  'PAYMENTINFO_0_TRANSACTIONID=7TR35978HS6402734&PAYMENTINFO_0_TRANSACTIONTYPE=expresscheckout&' \
                  'PAYMENTINFO_0_PAYMENTTYPE=instant&PAYMENTINFO_0_ORDERTIME=2014%2d12%2d14T10%3a49%3a42Z&' \
                  'PAYMENTINFO_0_AMT=23%2e99&PAYMENTINFO_0_TAXAMT=0%2e00&PAYMENTINFO_0_CURRENCYCODE=EUR&' \
                  'PAYMENTINFO_0_PAYMENTSTATUS=Pending&PAYMENTINFO_0_PENDINGREASON=multicurrency&' \
                  'PAYMENTINFO_0_REASONCODE=None&PAYMENTINFO_0_PROTECTIONELIGIBILITY=Eligible&' \
                  'PAYMENTINFO_0_PROTECTIONELIGIBILITYTYPE=ItemNotReceivedEligible%2cUnauthorizedPaymentEligible&' \
                  'PAYMENTINFO_0_SECUREMERCHANTACCOUNTID=N7DUXYBV52FQ4&PAYMENTINFO_0_ERRORCODE=0&' \
                  'PAYMENTINFO_0_ACK=Success'

    def perform_action(self):
        self.add_product_to_basket(price=D('23.99'))
        basket = Basket.objects.first()
        basket.freeze()

        self.url = reverse('paypal-handle-order', kwargs={'basket_id': basket.id})
        url = URL().path(self.url) \
            .query_param('PayerID', 'Y8K3PSJYN24D4') \
            .query_param('token', 'EC-7F151994RW7618524')
        self.response = self.client.get(str(url), follow=True)
        self.order = Order.objects.first()

    def test_order_total(self):
        self.assertEqual(D('23.99'), self.order.total_incl_tax)

    def test_order_email_address(self):
        self.assertEqual('info-buyer@test.com', self.order.guest_email)

    def test_order_includes_shipping(self):
        self.assertEqual('line2', self.order.shipping_address.line2)

    def test_post_should_is_a_bad_request(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 400)


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
        get_response = 'TOKEN=EC%2d6WY34243AN3588740&CHECKOUTSTATUS=PaymentActionCompleted' \
                       '&TIMESTAMP=2012%2d04%2d19T10%3a07%3a46Z&CORRELATIONID=7e9c5efbda3c0&ACK=Success' \
                       '&VERSION=88%2e0&BUILD=2808426&EMAIL=david%2e_1332854868_per%40gmail%2ecom' \
                       '&PAYERID=7ZTRBDFYYA47W&PAYERSTATUS=verified&FIRSTNAME=David&LASTNAME=Winterbottom' \
                       '&COUNTRYCODE=GB&SHIPTONAME=David%20Winterbottom&SHIPTOSTREET=1%20Main%20Terrace' \
                       '&SHIPTOSTREET2=line2&SHIPTOCITY=Wolverhampton&SHIPTOSTATE=West%20Midlands' \
                       '&SHIPTOZIP=W12%204LQ&SHIPTOCOUNTRYCODE=GB&SHIPTOCOUNTRYNAME=United%20Kingdom' \
                       '&ADDRESSSTATUS=Confirmed&CURRENCYCODE=GBP&AMT=33%2e98&SHIPPINGAMT=0%2e00' \
                       '&HANDLINGAMT=0%2e00&TAXAMT=0%2e00&INSURANCEAMT=0%2e00&SHIPDISCAMT=0%2e00' \
                       '&PAYMENTREQUEST_0_CURRENCYCODE=GBP&PAYMENTREQUEST_0_AMT=33%2e98' \
                       '&PAYMENTREQUEST_0_SHIPPINGAMT=0%2e00&PAYMENTREQUEST_0_HANDLINGAMT=0%2e00' \
                       '&PAYMENTREQUEST_0_TAXAMT=0%2e00&PAYMENTREQUEST_0_INSURANCEAMT=0%2e00' \
                       '&PAYMENTREQUEST_0_SHIPDISCAMT=0%2e00&PAYMENTREQUEST_0_TRANSACTIONID=51963679RW630412N' \
                       '&PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false' \
                       '&PAYMENTREQUEST_0_SHIPTONAME=David%20Winterbottom' \
                       '&PAYMENTREQUEST_0_SHIPTOSTREET=1%20Main%20Terrace&PAYMENTREQUEST_0_SHIPTOSTREET2=line2' \
                       '&PAYMENTREQUEST_0_SHIPTOCITY=Wolverhampton&PAYMENTREQUEST_0_SHIPTOSTATE=West%20Midlands' \
                       '&PAYMENTREQUEST_0_SHIPTOZIP=W12%204LQ&PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE=GB' \
                       '&PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME=United%20Kingdom' \
                       '&PAYMENTREQUESTINFO_0_TRANSACTIONID=51963679RW630412N' \
                       '&PAYMENTREQUESTINFO_0_ERRORCODE=0'   # noqa E501
        error_response = 'Error'

        def side_effect(url, payload, **kwargs):
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
