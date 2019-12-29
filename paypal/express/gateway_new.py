import logging
from decimal import Decimal as D

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import striptags, truncatechars

from paypalcheckoutsdk.core import LiveEnvironment, PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCaptureRequest, OrdersCreateRequest, OrdersGetRequest
from paypalcheckoutsdk.payments import AuthorizationsVoidRequest, CapturesRefundRequest

from .models import ExpressCheckoutTransaction


logger = logging.getLogger('paypal.express')

INTENT_AUTHORIZE = 'AUTHORIZE'
INTENT_CAPTURE = 'CAPTURE'

LANDING_PAGE_LOGIN = 'LOGIN'
LANDING_PAGE_BILLING = 'BILLING'
LANDING_PAGE_NO_PREFERENCE = 'NO_PREFERENCE'

USER_ACTION_CONTINUE = 'CONTINUE'
USER_ACTION_PAY_NOW = 'PAY_NOW'


def format_description(description):
    return truncatechars(striptags(description), 127) if description else ''


def format_amount(amount):
    return str(amount.quantize(D('0.01')))


def get_intent():
    intent = getattr(settings, 'PAYPAL_ORDER_INTENT', INTENT_CAPTURE)
    if intent not in (INTENT_AUTHORIZE, INTENT_CAPTURE):
        raise ImproperlyConfigured('{} is not a valid order intent'.format(intent))
    return intent


def get_landing_page():
    landing_page = getattr(settings, 'PAYPAL_LANDING_PAGE', LANDING_PAGE_NO_PREFERENCE)
    if landing_page not in (LANDING_PAGE_LOGIN, LANDING_PAGE_BILLING, LANDING_PAGE_NO_PREFERENCE):
        raise ImproperlyConfigured('{} is not a valid landing page'.format(landing_page))
    return landing_page


def get_user_action():
    user_action = getattr(settings, 'PAYPAL_USER_ACTION', USER_ACTION_PAY_NOW)
    if user_action not in (USER_ACTION_CONTINUE, USER_ACTION_PAY_NOW):
        raise ImproperlyConfigured('{} is not a valid user action'.format(user_action))
    return user_action


class PaymentProcessor:

    def __init__(self):
        credentials = {
            'client_id': settings.PAYPAL_SANDBOX_CLIENT_ID,
            'client_secret': settings.PAYPAL_SANDBOX_CLIENT_SECRET,
        }

        if getattr(settings, 'PAYPAL_SANDBOX_MODE', True):
            environment = SandboxEnvironment(**credentials)
        else:
            environment = LiveEnvironment(**credentials)

        self.client = PayPalHttpClient(environment)

    def build_order_create_request_body(
            self, basket, currency, return_url, cancel_url,
            intent=None, user=None, user_address=None, shipping_address=None, shipping_method=None, no_shipping=False,
    ):
        intent = intent or get_intent()

        application_context = {
            'return_url': return_url,
            'cancel_url': cancel_url,
            'landing_page': get_landing_page(),
            'shipping_preference': 'NO_SHIPPING' if no_shipping else 'SET_PROVIDED_ADDRESS',  # TODO: ???
            'user_action': get_user_action(),
        }

        if getattr(settings, 'PAYPAL_BRAND_NAME', None) is not None:
            application_context['brand_name'] = settings.PAYPAL_BRAND_NAME

        shipping_charge = None
        order_total = basket.total_incl_tax
        if shipping_method:
            shipping_charge = shipping_method.calculate(basket).incl_tax
            order_total += shipping_charge

        breakdown = {
            'item_total': {
                'currency_code': currency,
                'value': format_amount(basket.total_incl_tax),
            },
        }

        if shipping_charge is not None:
            breakdown['shipping'] = {
                'currency_code': currency,
                'value': format_amount(shipping_charge),
            }

        purchase_unit = {
            'amount': {
                'currency_code': currency,
                'value': format_amount(order_total),
                'breakdown': breakdown,
            }
        }

        items = []
        for line in basket.all_lines():
            product = line.product
            item = {
                'name': product.get_title(),
                'description': format_description(product.description),
                'sku': product.upc if product.upc else '',
                'unit_amount': {
                    'currency_code': currency,
                    'value': format_amount(line.unit_price_incl_tax)
                },
                'quantity': line.quantity,
                'category': 'PHYSICAL_GOODS' if product.is_shipping_required else 'DIGITAL_GOODS'
            }
            items.append(item)

        purchase_unit['items'] = items

        name = address = None
        if shipping_address:
            name = shipping_address.name
            address = {
                'address_line_1': shipping_address.line1,
                'address_line_2': shipping_address.line2,
                'admin_area_2': shipping_address.line4,
                'admin_area_1': shipping_address.state,
                'postal_code': shipping_address.postcode,
                'country_code': shipping_address.country.iso_3166_1_a2
            }
        elif user_address:
            name = user_address.name
            address = {
                'address_line_1': user_address.line1,
                'address_line_2': user_address.line2,
                'admin_area_2': user_address.line4,
                'admin_area_1': user_address.state,
                'postal_code': user_address.postcode,
                'country_code': user_address.country.iso_3166_1_a2
            }
        if name is not None and address is not None:
            purchase_unit['shipping'] = {
                'name': {
                    'full_name': name
                },
                'address': address
            }

        body = {
            'intent': intent,
            'application_context': application_context,
            'purchase_units': [purchase_unit]
        }
        return body

    def build_refund_order_request_body(self, amount, currency):
        return {
            'amount': {
                'value': format_amount(amount),
                'currency_code': currency
            }
        }

    def create_order(
            self, basket, currency, return_url, cancel_url,
            user=None, user_address=None, shipping_address=None, shipping_method=None, no_shipping=None, intent=None,
    ):

        request = OrdersCreateRequest()
        request.prefer('return=representation')  # TODO: probably here we can use default `prefer`?
        request.request_body(self.build_order_create_request_body(
            basket=basket,
            currency=currency,
            return_url=return_url,
            cancel_url=cancel_url,
            user=user,
            user_address=user_address,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            no_shipping=no_shipping,
        ))
        response = self.client.execute(request)

        result = response.result
        # tnx = ExpressCheckoutTransaction(
        #     token=result.id,
        #     status=result.status,
        #     intent=intent,
        #     amount=basket.total_incl_tax,
        #     currency=currency,
        # )

        for link in response.result.links:
            if link.rel == 'approve':
                return link.href

    def get_order(self, token):
        request = OrdersGetRequest(token)
        response = self.client.execute(request)
        return response.result

    def void_authorized_order(self, token):
        request = AuthorizationsVoidRequest(token)
        response = self.client.execute(request)
        return response.result

    def refund_order(self, token, amount, currency):
        request = CapturesRefundRequest(token)
        request.prefer('return=representation')  # TODO: probably here we can use default `prefer`?
        request.request_body(self.build_refund_order_request_body(amount, currency))
        response = self.client.execute(request)
        return response.result

    def capture_order(self, token):  # TODO: `capture_approved_order` ?
        request = OrdersCaptureRequest(token)
        response = self.client.execute(request)
        return response.result
