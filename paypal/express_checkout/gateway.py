from decimal import Decimal as D

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import striptags, truncatechars
from django.utils.translation import gettext_lazy as _
from paypalcheckoutsdk.core import LiveEnvironment, PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import (
    OrdersAuthorizeRequest, OrdersCaptureRequest, OrdersCreateRequest, OrdersGetRequest)
from paypalcheckoutsdk.payments import AuthorizationsCaptureRequest, AuthorizationsVoidRequest, CapturesRefundRequest

INTENT_AUTHORIZE = 'AUTHORIZE'
INTENT_CAPTURE = 'CAPTURE'

INTENT_REQUEST_MAPPING = {
    INTENT_AUTHORIZE: AuthorizationsCaptureRequest,
    INTENT_CAPTURE: OrdersCaptureRequest,
}

LANDING_PAGE_LOGIN = 'LOGIN'
LANDING_PAGE_BILLING = 'BILLING'
LANDING_PAGE_NO_PREFERENCE = 'NO_PREFERENCE'

USER_ACTION_CONTINUE = 'CONTINUE'
USER_ACTION_PAY_NOW = 'PAY_NOW'

buyer_pays_on_paypal = lambda: getattr(settings, 'PAYPAL_BUYER_PAYS_ON_PAYPAL', False)


def format_description(description):
    return truncatechars(striptags(description), 127) if description else ''


def format_amount(amount):
    return str(amount.quantize(D('0.01')))


def get_landing_page():
    landing_page = getattr(settings, 'PAYPAL_LANDING_PAGE', LANDING_PAGE_NO_PREFERENCE)
    if landing_page not in (LANDING_PAGE_LOGIN, LANDING_PAGE_BILLING, LANDING_PAGE_NO_PREFERENCE):
        message = _("'%s' is not a valid landing page") % landing_page
        raise ImproperlyConfigured(message)
    return landing_page


class PaymentProcessor:
    client = None

    def __init__(self):
        credentials = {
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
        }

        if getattr(settings, 'PAYPAL_SANDBOX_MODE', True):
            environment = SandboxEnvironment(**credentials)
        else:
            environment = LiveEnvironment(**credentials)

        self.client = PayPalHttpClient(environment)

    def build_order_create_request_body(
            self, basket, currency, return_url, cancel_url, order_total,
            address=None, shipping_charge=None, intent=None,
    ):
        application_context = {
            'return_url': return_url,
            'cancel_url': cancel_url,
            'landing_page': get_landing_page(),
            'shipping_preference': 'SET_PROVIDED_ADDRESS' if address is not None else 'NO_SHIPPING',  # TODO: ???
            'user_action': 'PAY_NOW' if buyer_pays_on_paypal() else 'CONTINUE',
        }

        if getattr(settings, 'PAYPAL_BRAND_NAME', None) is not None:
            application_context['brand_name'] = settings.PAYPAL_BRAND_NAME

        breakdown = {
            'item_total': {
                'currency_code': currency,
                'value': format_amount(basket.total_incl_tax_excl_discounts),
            },
            'discount': {
                'currency_code': currency,
                'value': format_amount(sum([
                    discount['discount']
                    for discount
                    in basket.offer_discounts + basket.voucher_discounts
                ], D(0))),
            },
            'shipping_discount': {
                'currency_code': currency,
                'value': format_amount(sum([
                    discount['discount']
                    for discount
                    in basket.shipping_discounts
                ], D(0))),
            }
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

        if address is not None:
            purchase_unit['shipping'] = {
                'name': {
                    'full_name': address.name
                },
                'address': {
                    'address_line_1': address.line1,
                    'address_line_2': address.line2,
                    'admin_area_2': address.line4,
                    'admin_area_1': address.state,
                    'postal_code': address.postcode,
                    'country_code': address.country.iso_3166_1_a2
                }
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
            self, basket, currency, return_url, cancel_url, order_total,
            address=None, shipping_charge=None, intent=None, preferred_response='minimal',
    ):
        request = OrdersCreateRequest()
        request.prefer(f'return={preferred_response}')
        request.request_body(self.build_order_create_request_body(
            basket=basket,
            currency=currency,
            return_url=return_url,
            cancel_url=cancel_url,
            order_total=order_total,
            intent=intent,
            address=address,
            shipping_charge=shipping_charge,
        ))
        response = self.client.execute(request)
        return response.result

    def get_order(self, token):
        request = OrdersGetRequest(token)
        response = self.client.execute(request)
        return response.result

    def get_authorize_request_body(self):
        return {}

    def authorize_order(self, order_id, preferred_response='minimal'):
        request = OrdersAuthorizeRequest(order_id)
        request.prefer(f'return={preferred_response}')
        request.request_body(self.get_authorize_request_body())
        response = self.client.execute(request)
        return response.result

    def void_authorized_order(self, authorization_id):
        request = AuthorizationsVoidRequest(authorization_id)
        self.client.execute(request)

    def refund_order(self, capture_id, amount, currency, preferred_response='minimal'):
        request = CapturesRefundRequest(capture_id)
        request.prefer(f'return={preferred_response}')
        request.request_body(self.build_refund_order_request_body(amount, currency))
        response = self.client.execute(request)
        return response.result

    def capture_order(self, token, intent, preferred_response='minimal'):
        capture_request = INTENT_REQUEST_MAPPING[intent]
        request = capture_request(token)
        request.prefer(f'return={preferred_response}')
        response = self.client.execute(request)
        return response.result
