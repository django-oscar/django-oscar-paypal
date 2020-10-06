from decimal import Decimal as D
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from oscar.apps.basket.models import Basket
from oscar.apps.checkout.utils import CheckoutSessionData
from oscar.apps.order.models import Order
from oscar.test.factories import create_product

from paypalhttp.http_error import HttpError
from paypalhttp.http_response import construct_object

from paypal.express_checkout.models import ExpressCheckoutTransaction
from tests.shipping.methods import SecondClassRecorded
from .mocked_data import CAPTURE_ORDER_RESULT_DATA_MINIMAL, CREATE_ORDER_RESULT_DATA_MINIMAL, GET_ORDER_RESULT_DATA


class BasketMixin:

    def add_product_to_basket(self, price=D('100.00')):
        product = create_product(price=price, num_in_stock=1)
        url = reverse('basket:add', kwargs={'pk': product.pk})
        self.client.post(url, {'quantity': 1})


class EdgeCaseTests(BasketMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('paypal-redirect')

    def test_empty_basket_shows_error(self):
        response = self.client.get(self.url)
        assert reverse('basket:summary') == response.url

    def test_missing_shipping_address(self):
        from paypal.express_checkout.views import PaypalRedirectView
        with patch.object(PaypalRedirectView, 'as_payment_method') as as_payment_method:
            as_payment_method.return_value = True

            self.add_product_to_basket()
            response = self.client.get(self.url)
            assert reverse('checkout:shipping-address') == response.url

    def test_missing_shipping_method(self):
        from paypal.express_checkout.views import PaypalRedirectView

        with patch.object(PaypalRedirectView, 'as_payment_method') as as_payment_method:
            with patch.object(PaypalRedirectView, 'get_shipping_address') as get_shipping_address:
                with patch.object(PaypalRedirectView, 'get_shipping_method') as get_shipping_method:

                    as_payment_method.return_value = True
                    get_shipping_address.return_value = Mock()
                    get_shipping_method.return_value = None

                    self.add_product_to_basket()
                    response = self.client.get(self.url)
                    assert reverse('checkout:shipping-method') == response.url


class RedirectToPayPalTests(BasketMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('paypal-redirect')

    def test_nonempty_basket_redirects_to_paypal(self):
        order_approve_url = 'https://www.sandbox.paypal.com/checkoutnow?token=4MW805572N795704B'

        with patch('paypal.express_checkout.gateway.PaymentProcessor.create_order') as create_order:
            create_order.return_value = construct_object('Result', CREATE_ORDER_RESULT_DATA_MINIMAL)

            self.add_product_to_basket()
            response = self.client.get(self.url)
            assert response.url == order_approve_url

    def test_paypal_error_redirects_to_basket(self):
        with patch('paypal.express_checkout.gateway.PaymentProcessor.create_order') as create_order:
            create_order.side_effect = HttpError(message='Error message', status_code=404, headers=None)

            self.add_product_to_basket()
            response = self.client.get(self.url)
            assert reverse('basket:summary') == response.url


class PreviewOrderTests(BasketMixin, TestCase):
    fixtures = ['countries.json']

    def setUp(self):
        super().setUp()

        self.add_product_to_basket(price=D('9.99'))
        basket = Basket.objects.all().first()
        basket.freeze()

        url = reverse('paypal-success-response', kwargs={'basket_id': basket.id})
        query_string = urlencode({'PayerID': '0000000000001', 'token': '4MW805572N795704B'})
        self.url_with_query_string = f'{url}?{query_string}'

        # Imitate selecting of shipping method in `form_valid` method of `ShippingMethodView`
        session = self.client.session
        session[CheckoutSessionData.SESSION_KEY] = {'shipping': {'method_code': SecondClassRecorded.code}}
        session.save()

        # Before preview order must be created
        ExpressCheckoutTransaction.objects.create(
            order_id='4MW805572N795704B',
            amount=D('19.99'),
            currency=basket.currency,
            status=ExpressCheckoutTransaction.CREATED,
            intent=ExpressCheckoutTransaction.CAPTURE,
        )

    def test_context(self):
        with patch('paypal.express_checkout.gateway.PaymentProcessor.get_order') as get_order:
            get_order.return_value = construct_object('Result', GET_ORDER_RESULT_DATA)

            response = self.client.get(self.url_with_query_string, follow=True)

            context = response.context
            assert D('19.99') == context['paypal_amount']
            assert 'Royal Mail Signed For™ 2nd Class' == context['shipping_method'].name
            assert 'uk_rm_2ndrecorded' == context['shipping_method'].code

            keys = ('shipping_address', 'shipping_method', 'payer_id', 'token', 'paypal_user_email', 'paypal_amount')
            for k in keys:
                assert k in context, f'{k} not in context'

    def test_paypal_error_redirects_to_basket(self):
        self.add_product_to_basket(price=D('9.99'))
        basket = Basket.objects.all().first()
        basket.freeze()

        with patch('paypal.express_checkout.gateway.PaymentProcessor.get_order') as get_order:
            get_order.side_effect = HttpError(message='Error message', status_code=404, headers=None)

            response = self.client.get(self.url_with_query_string)
            assert reverse('basket:summary') == response.url


class SubmitOrderTests(BasketMixin, TestCase):
    fixtures = ['countries.json']

    def setUp(self):
        super().setUp()

        self.add_product_to_basket(price=D('9.99'))
        basket = Basket.objects.all().first()
        basket.freeze()

        self.url = reverse('paypal-place-order', kwargs={'basket_id': basket.id})
        self.payload = {
            'action': 'place_order',
            'payer_id': '0000000000001',
            'token': '4MW805572N795704B',
        }

        # Imitate selecting of shipping method in `form_valid` method of `ShippingMethodView`
        session = self.client.session
        session[CheckoutSessionData.SESSION_KEY] = {'shipping': {'method_code': SecondClassRecorded.code}}
        session.save()

        # Before getting order must be created
        ExpressCheckoutTransaction.objects.create(
            order_id='4MW805572N795704B',
            amount=D('19.99'),
            currency=basket.currency,
            status=ExpressCheckoutTransaction.CREATED,
            intent=ExpressCheckoutTransaction.CAPTURE,
        )

    def test_created_order(self):
        with patch('paypal.express_checkout.gateway.PaymentProcessor.get_order') as get_order:
            with patch('paypal.express_checkout.gateway.PaymentProcessor.capture_order') as capture_order:

                get_order.return_value = construct_object('Result', GET_ORDER_RESULT_DATA)
                capture_order.return_value = construct_object('Result', CAPTURE_ORDER_RESULT_DATA_MINIMAL)

                self.client.post(self.url, self.payload)

                order = Order.objects.all().first()
                assert order.total_incl_tax == D('9.99')
                assert order.guest_email == 'sherlock.holmes@example.com'

                address = order.shipping_address
                assert address.line1 == '221B Baker Street'
                assert address.line4 == 'London'
                assert address.country.iso_3166_1_a2 == 'GB'
                assert address.postcode == 'WC2N 5DU'

    def test_paypal_error(self):
        with patch('paypal.express_checkout.gateway.PaymentProcessor.get_order') as get_order:
            with patch('paypal.express_checkout.gateway.PaymentProcessor.capture_order') as capture_order:

                get_order.return_value = construct_object('Result', GET_ORDER_RESULT_DATA)
                capture_order.side_effect = HttpError(message='Error message', status_code=404, headers=None)

                response = self.client.post(self.url, self.payload)
                expected_message = 'A problem occurred during payment capturing - please try again later'
                assert expected_message in response.content.decode()


class CancelOrderTests(BasketMixin, TestCase):

    def test_cancel_order(self):
        """
        In case of order cancellation on PayPay side, a user will be redirected
        to the URL like ".../en-gb/checkout/paypal/cancel/<basket_id>/?token=43V282428E5567001"
        """

        self.add_product_to_basket(price=D('9.99'))
        basket = Basket.objects.all().first()
        basket.freeze()

        url = reverse('paypal-cancel-response', kwargs={'basket_id': basket.id})
        response = self.client.get(url, follow=True)
        assert 'PayPal transaction cancelled' in response.content.decode()
