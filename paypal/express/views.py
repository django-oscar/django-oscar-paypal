import logging
from decimal import Decimal as D

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView, View
from oscar.apps.payment.exceptions import UnableToTakePayment
from oscar.apps.shipping.methods import FixedPrice, NoShippingRequired
from oscar.core.exceptions import ModuleNotFoundError
from oscar.core.loading import get_class, get_model
from paypalhttp.http_error import HttpError

from paypal.exceptions import PayPalError
from paypal.express.exceptions import (
    EmptyBasketException, InvalidBasket, MissingShippingAddressException, MissingShippingMethodException)
from paypal.express.facade import get_paypal_url
from paypal.express.gateway_new import PaymentProcessor

# Load views dynamically
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')
Basket = get_model('basket', 'Basket')
Repository = get_class('shipping.repository', 'Repository')
Selector = get_class('partner.strategy', 'Selector')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
try:
    Applicator = get_class('offer.applicator', 'Applicator')
except ModuleNotFoundError:
    # fallback for django-oscar<=1.1
    Applicator = get_class('offer.utils', 'Applicator')

logger = logging.getLogger('paypal.express')


class RedirectView(CheckoutSessionMixin, RedirectView):
    """
    Initiate the transaction with Paypal and redirect the user
    to PayPal's Express Checkout to perform the transaction.
    """
    permanent = False

    # Setting to distinguish if the site has already collected a shipping
    # address.  This is False when redirecting to PayPal straight from the
    # basket page but True when redirecting from checkout.
    as_payment_method = False

    def get_redirect_url(self, **kwargs):
        try:
            basket = self.build_submission()['basket']
            url = self._get_redirect_url(basket, **kwargs)
        except HttpError as e:
            messages.error(self.request, e.message)
            if self.as_payment_method:
                url = reverse('checkout:payment-details')
            else:
                url = reverse('basket:summary')
            return url
        except InvalidBasket as e:
            messages.warning(self.request, str(e))
            return reverse('basket:summary')
        except EmptyBasketException:
            messages.error(self.request, _("Your basket is empty"))
            return reverse('basket:summary')
        except MissingShippingAddressException:
            messages.error(
                self.request, _("A shipping address must be specified"))
            return reverse('checkout:shipping-address')
        except MissingShippingMethodException:
            messages.error(
                self.request, _("A shipping method must be specified"))
            return reverse('checkout:shipping-method')
        else:
            # Transaction successfully registered with PayPal.  Now freeze the
            # basket so it can't be edited while the customer is on the PayPal
            # site.
            basket.freeze()

            logger.info('Basket #%s - redirecting to %s', basket.id, url)

            return url

    def _get_redirect_url(self, basket, **kwargs):
        if basket.is_empty:
            raise EmptyBasketException()

        params = {'basket': basket}

        user = self.request.user
        if self.as_payment_method:
            if basket.is_shipping_required():
                # Only check for shipping details if required.
                shipping_addr = self.get_shipping_address(basket)
                if not shipping_addr:
                    raise MissingShippingAddressException()

                shipping_method = self.get_shipping_method(basket, shipping_addr)
                if not shipping_method:
                    raise MissingShippingMethodException()

                params['shipping_address'] = shipping_addr
                params['shipping_method'] = shipping_method

        if settings.DEBUG:
            # Determine the local server's hostname to use when in testing mode
            params['host'] = self.request.META['HTTP_HOST']

        if user.is_authenticated:
            params['user'] = user

        return get_paypal_url(**params)


class CancelResponseView(RedirectView):
    permanent = False

    def get(self, request, *args, **kwargs):
        basket = get_object_or_404(Basket, id=kwargs['basket_id'],
                                   status=Basket.FROZEN)
        basket.thaw()
        logger.info("Payment cancelled (token %s) - basket #%s thawed",
                    request.GET.get('token', '<no token>'), basket.id)
        return super(CancelResponseView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        messages.error(self.request, _("PayPal transaction cancelled"))
        return reverse('basket:summary')


# Upgrading notes: when we drop support for Oscar 0.6, this class can be
# refactored to pass variables around more explicitly (instead of assigning
# things to self so they are accessible in a later method).
class SuccessResponseView(PaymentDetailsView):
    template_name_preview = 'paypal/express/preview.html'
    preview = True

    @property
    def pre_conditions(self):
        return []

    def get(self, request, *args, **kwargs):
        """
        Fetch details about the successful transaction from PayPal.  We use
        these details to show a preview of the order with a 'submit' button to
        place it.
        """
        try:
            self.payer_id = request.GET['PayerID']
            self.token = request.GET['token']
        except KeyError:
            # Manipulation - redirect to basket page with warning message
            logger.warning('Missing GET params on success response page')
            messages.error(self.request, _('Unable to determine PayPal transaction details'))
            return HttpResponseRedirect(reverse('basket:summary'))

        try:
            self.txn = PaymentProcessor().get_order(self.token)
        except HttpError as e:
            messages.error(self.request, e.message)
            logger.warning('Unable to fetch transaction details for token %s: %s', self.token, e.message)
            message = _('A problem occurred communicating with PayPal - please try again later')
            messages.error(self.request, message)
            return HttpResponseRedirect(reverse('basket:summary'))

        # Reload frozen basket which is specified in the URL
        kwargs['basket'] = self.load_frozen_basket(kwargs['basket_id'])
        if not kwargs['basket']:
            logger.warning('Unable to load frozen basket with ID %s', kwargs['basket_id'])
            message = _('No basket was found that corresponds to your PayPal transaction')
            messages.error(self.request, message)
            return HttpResponseRedirect(reverse('basket:summary'))

        logger.info(
            'Basket #%s - showing preview with payer ID %s and token %s',
            kwargs['basket'].id, self.payer_id, self.token)

        return super().get(request, *args, **kwargs)

    def load_frozen_basket(self, basket_id):
        # Lookup the frozen basket that this txn corresponds to
        try:
            basket = Basket.objects.get(id=basket_id, status=Basket.FROZEN)
        except Basket.DoesNotExist:
            return None

        # Assign strategy to basket instance
        if Selector:
            basket.strategy = Selector().strategy(self.request)

        # Re-apply any offers
        Applicator().apply(basket, self.request.user, request=self.request)

        return basket

    def get_context_data(self, **kwargs):
        ctx = super(SuccessResponseView, self).get_context_data(**kwargs)

        if not hasattr(self, 'payer_id'):
            return ctx

        # This context generation only runs when in preview mode
        ctx.update({
            'payer_id': self.payer_id,
            'token': self.token,
            'paypal_user_email': self.txn['payer']['email_address'],
            'paypal_amount': D(self.txn['purchase_units'][0]['amount']['value']),
        })

        return ctx

    def post(self, request, *args, **kwargs):
        """
        Place an order.

        We fetch the txn details again and then proceed with oscar's standard
        payment details view for placing the order.
        """
        error_msg = _(
            "A problem occurred communicating with PayPal - please try again later"
        )
        try:
            self.payer_id = request.POST['payer_id']
            self.token = request.POST['token']
        except KeyError:
            # Probably suspicious manipulation if we get here
            messages.error(self.request, error_msg)
            return HttpResponseRedirect(reverse('basket:summary'))

        try:
            self.txn = PaymentProcessor().get_order(self.token)
        except PayPalError:
            # Unable to fetch txn details from PayPal - we have to bail out
            messages.error(self.request, error_msg)
            return HttpResponseRedirect(reverse('basket:summary'))

        # Reload frozen basket which is specified in the URL
        basket = self.load_frozen_basket(kwargs['basket_id'])
        if not basket:
            messages.error(self.request, error_msg)
            return HttpResponseRedirect(reverse('basket:summary'))

        submission = self.build_submission(basket=basket)
        return self.submit(**submission)

    def build_submission(self, **kwargs):
        submission = super().build_submission(**kwargs)
        # Pass the user email so it can be stored with the order
        submission['order_kwargs']['guest_email'] = self.txn['payer']['email_address']
        # Pass PP params
        submission['payment_kwargs']['payer_id'] = self.payer_id
        submission['payment_kwargs']['token'] = self.token
        submission['payment_kwargs']['txn'] = self.txn
        return submission

    def handle_payment(self, order_number, total, **kwargs):
        """
        Complete payment with PayPal - this calls the 'DoExpressCheckout'
        method to capture the money from the initial transaction.
        """
        try:
            confirm_txn = PaymentProcessor().capture_order(self.txn['id'])
        except HttpError:
            raise UnableToTakePayment()
        if not confirm_txn['status'] == 'COMPLETED':
            raise UnableToTakePayment()

        # Record payment source and event
        source_type, is_created = SourceType.objects.get_or_create(name='PayPal')
        currency = confirm_txn['purchase_units'][0]['payments']['captures'][0]['amount']['currency_code']
        amount = D(confirm_txn['purchase_units'][0]['payments']['captures'][0]['amount']['value'])
        source = Source(
            source_type=source_type,
            currency=currency,
            amount_allocated=amount,
            amount_debited=amount
        )
        self.add_payment_source(source)
        self.add_payment_event('Settled', amount, reference=confirm_txn['id'])

    def get_shipping_address(self, basket):
        """
        Return a created shipping address instance, created using
        the data returned by PayPal.
        """
        ship_to_name = self.txn.purchase_units[0].shipping.name.full_name
        if ship_to_name is None:
            return None
        first_name = last_name = ''
        parts = ship_to_name.split()
        if len(parts) == 1:
            last_name = ship_to_name
        elif len(parts) > 1:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])

        address = self.txn['purchase_units'][0]['shipping']['address']
        return ShippingAddress(
            first_name=first_name,
            last_name=last_name,
            line1=address['address_line_1'],
            line2=address.get('address_line_2', ''),
            line4=address['admin_area_2'],
            state=address.get('admin_area_1', ''),
            postcode=address['postal_code'],
            country=Country.objects.get(iso_3166_1_a2=address['country_code']),
            # phone_number=self.txn.value('PAYMENTREQUEST_0_SHIPTOPHONENUM', default=""),
        )

    def _get_shipping_method_by_name(self, name, basket, shipping_address=None):
        methods = Repository().get_shipping_methods(
            basket=basket, user=self.request.user,
            shipping_addr=shipping_address, request=self.request)
        for method in methods:
            if method.name == name:
                return method

    def get_shipping_method(self, basket, shipping_address=None, **kwargs):
        """
        Return the shipping method used
        """
        if not basket.is_shipping_required():
            return NoShippingRequired()

        return super().get_shipping_method(basket, shipping_address, **kwargs)


class ShippingOptionsView(View):

    def get(self, request, *args, **kwargs):
        """
        We use the shipping address given to use by PayPal to
        determine the available shipping method
        """
        # Basket ID is passed within the URL path.  We need to do this as some
        # shipping options depend on the user and basket contents.  PayPal do
        # pass back details of the basket contents but it would be royal pain to
        # reconstitute the basket based on those - easier to just to piggy-back
        # the basket ID in the callback URL.
        basket = get_object_or_404(Basket, id=kwargs['basket_id'])
        user = basket.owner
        if not user:
            user = AnonymousUser()

        # Create a shipping address instance using the data passed back
        country_code = self.request.GET.get(
            'SHIPTOCOUNTRY', None)
        try:
            country = Country.objects.get(iso_3166_1_a2=country_code)
        except Country.DoesNotExist:
            country = Country()

        shipping_address = ShippingAddress(
            line1=self.request.GET.get('SHIPTOSTREET', ''),
            line2=self.request.GET.get('SHIPTOSTREET2', ''),
            line4=self.request.GET.get('SHIPTOCITY', ''),
            state=self.request.GET.get('SHIPTOSTATE', ''),
            postcode=self.request.GET.get('SHIPTOZIP', ''),
            country=country
        )
        methods = Repository().get_shipping_methods(
            basket=basket, shipping_addr=shipping_address,
            request=self.request, user=user)
        return self.render_to_response(methods, basket)

    def post(self, request, *args, **kwargs):
        """
        We use the shipping address given to use by PayPal to
        determine the available shipping method
        """
        # Basket ID is passed within the URL path.  We need to do this as some
        # shipping options depend on the user and basket contents.  PayPal do
        # pass back details of the basket contents but it would be royal pain to
        # reconstitute the basket based on those - easier to just to piggy-back
        # the basket ID in the callback URL.
        basket = get_object_or_404(Basket, id=kwargs['basket_id'])
        user = basket.owner
        if not user:
            user = AnonymousUser()

        # Create a shipping address instance using the data passed back
        country_code = self.request.POST.get(
            'SHIPTOCOUNTRY', None)
        try:
            country = Country.objects.get(iso_3166_1_a2=country_code)
        except Country.DoesNotExist:
            country = Country()

        shipping_address = ShippingAddress(
            line1=self.request.POST.get('SHIPTOSTREET', ''),
            line2=self.request.POST.get('SHIPTOSTREET2', ''),
            line4=self.request.POST.get('SHIPTOCITY', ''),
            state=self.request.POST.get('SHIPTOSTATE', ''),
            postcode=self.request.POST.get('SHIPTOZIP', ''),
            country=country
        )
        methods = Repository().get_shipping_methods(
            basket=basket, shipping_addr=shipping_address,
            request=self.request, user=user)
        return self.render_to_response(methods, basket)

    def render_to_response(self, methods, basket):
        pairs = [
            ('METHOD', 'CallbackResponse'),
            ('CALLBACKVERSION', '61.0'),
            ('CURRENCYCODE', self.request.POST.get('CURRENCYCODE', 'GBP')),
        ]
        if methods:
            for index, method in enumerate(methods):
                charge = method.calculate(basket).incl_tax

                pairs.append(('L_SHIPPINGOPTIONNAME%d' % index,
                              str(method.name)))
                pairs.append(('L_SHIPPINGOPTIONLABEL%d' % index,
                              str(method.description)))
                pairs.append(('L_SHIPPINGOPTIONAMOUNT%d' % index, charge))
                # For now, we assume tax and insurance to be zero
                pairs.append(('L_TAXAMT%d' % index, D('0.00')))
                pairs.append(('L_INSURANCEAMT%d' % index, D('0.00')))
                # We assume that the first returned method is the default one
                pairs.append(('L_SHIPPINGOPTIONISDEFAULT%d' % index,
                              1 if index == 0 else 0))
        else:
            # No shipping methods available - we flag this up to PayPal indicating that we
            # do not ship to the shipping address.
            pairs.append(('NO_SHIPPING_OPTION_DETAILS', 1))

        payload = urlencode(pairs)
        logger.debug("Basket #%s - returning postage costs payload = '%s'", basket.id, payload)
        return HttpResponse(payload)
