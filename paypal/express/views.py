from decimal import Decimal as D

from django.views.generic import RedirectView
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import get_model

from oscar.apps.checkout.views import PaymentDetailsView
from oscar.apps.payment.exceptions import PaymentError, UnableToTakePayment
from oscar.apps.payment.models import SourceType, Source

from paypal.express.facade import get_paypal_url, fetch_transaction_details, confirm_transaction
from paypal.express import PayPalError

ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')


class RedirectView(RedirectView):
    """
    Initiate the transaction with Paypal and redirect the user 
    to PayPal's Express Checkout to perform the transaction.
    """
    permanent = False

    def get_redirect_url(self, **kwargs):
        try:
            return self._get_redirect_url(**kwargs)
        except PayPalError, e:
            messages.error(self.request, 
                           "You are unable to use PayPal for this order: %s" % e)
            return reverse('basket:summary')

    def _get_redirect_url(self, **kwargs):
        basket = self.request.basket
        if basket.is_empty:
            messages.error(self.request, "Your basket is empty")
            return reverse('basket:summary')

        params = {'basket': self.request.basket}
        if settings.DEBUG:
            # Determine the localserver's hostname to use when 
            # in testing mode
            params['host'] = self.request.META['HTTP_HOST']
            params['scheme'] = 'http'

        user = self.request.user
        if user.is_authenticated():
            params['user'] = user

        return get_paypal_url(**params)


class CancelResponseView(RedirectView):
    def get_redirect_url(self, **kwargs):
        messages.error(self.request, "PayPal transaction cancelled")
        return reverse('basket:summary')


class SuccessResponseView(PaymentDetailsView):
    template_name_preview = 'paypal/preview.html'

    def get(self, request, *args, **kwargs):
        """
        Fetch details about the successful transaction from 
        PayPal.  We use these details to show a preview of 
        the order with a 'submit' button to place it.
        """
        try:
            payer_id = request.GET['PayerID']
            token = request.GET['token']
        except KeyError:
            # Manipulation - redirect to basket page with warning message
            messages.error(self.request, "Unable to determine PayPal transaction details")
            return HttpResponseRedirect(reverse('basket:summary'))

        try:
            self.fetch_paypal_data(payer_id, token)
        except PayPalError:
            messages.error(self.request, "A problem occurred communicating with PayPal - please try again later")
            return HttpResponseRedirect(reverse('basket:summary'))
        return super(SuccessResponseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Place an order.

        We fetch the txn details again and then proceed with oscar's standard 
        payment details view for placing the order.
        """
        try:
            payer_id = request.POST['payer_id']
            token = request.POST['token']
        except KeyError:
            # Probably suspicious manipulation if we get here
            messages.error(self.request, "A problem occurred communicating with PayPal - please try again later")
            return HttpResponseRedirect(reverse('basket:summary'))
        try:
            self.fetch_paypal_data(payer_id, token)
        except PayPalError:
            # Unable to fetch txn details from PayPal - we have to bail out
            messages.error(self.request, "A problem occurred communicating with PayPal - please try again later")
            return HttpResponseRedirect(reverse('basket:summary'))

        # Pass the user email so it can be stored with the order
        kwargs['guest_email'] = self.txn.value('EMAIL')

        return super(SuccessResponseView, self).post(request, *args, **kwargs)

    def fetch_paypal_data(self, payer_id, token):
        self.payer_id = payer_id
        self.token = token
        self.txn = fetch_transaction_details(token)

    def get_error_response(self):
        # We bypass the normal session checks for shipping address and shipping
        # method as they don't apply here.

        # We do check that the order total is still the same as when we redirected 
        # off to PayPal
        txn_amount = self.txn.amount
        order_total = self.request.basket.total_incl_tax

        if txn_amount != order_total:
            messages.error(self.request, 
                           "Your order total (%s) differs from the total PayPal authorised (%s) - aborting" % (
                               order_total, txn_amount))
            return HttpResponseRedirect(reverse('basket:summary'))

    def get_context_data(self, **kwargs):
        ctx = super(SuccessResponseView, self).get_context_data(**kwargs)
        if not hasattr(self, 'payer_id'):
            return ctx
        ctx.update({
            'payer_id': self.payer_id,
            'token': self.token,
            'paypal_user_email': self.txn.value('EMAIL'),
            'paypal_amount': D(self.txn.value('AMT')),
        })
        # We convert the PayPal response values into those that match Oscar's normal
        # context so we can re-use the preview template as is
        shipping_address_fields = [
            self.txn.value('SHIPTONAME'),
            self.txn.value('SHIPTOSTREET'),
            self.txn.value('SHIPTOCITY'),
            self.txn.value('SHIPTOSTATE'),
            self.txn.value('SHIPTOZIP'),
            self.txn.value('SHIPTOCOUNTRYNAME'),
        ]
        ctx['shipping_address'] = {
            'active_address_fields': filter(bool, shipping_address_fields),
            'notes': self.txn.value('NOTETEXT'),
        }
        shipping_charge = D(self.txn.value('SHIPPINGAMT'))
        ctx['shipping_method'] = {
            'name': 'PayPal delivery',
            'description': 'Some description here',
            'basket_charge_incl_tax': shipping_charge,
        }
        ctx['order_total_incl_tax'] = self.request.basket.total_incl_tax + shipping_charge

        return ctx

    def handle_payment(self, order_number, total_incl_tax, **kwargs):
        """
        Complete payment with PayPal - this calls the 'DoExpressCheckout'
        method to capture the money from the initial transaction.
        """
        try:
            payer_id = self.request.POST['payer_id']
            token = self.request.POST['token']
        except KeyError:
            raise PaymentError("Unable to determine PayPal transaction details")

        try:
            txn = confirm_transaction(payer_id, token, amount=self.txn.amount,
                                      currency=self.txn.currency)
        except PayPalError:
            raise UnableToTakePayment()

        # Record payment source
        source_type, is_created = SourceType.objects.get_or_create(name='PayPal')
        source = Source(source_type=source_type,
                        currency=txn.currency,
                        amount_allocated=txn.amount,
                        amount_debited=txn.amount)
        self.add_payment_source(source)

    def create_shipping_address(self):
        """
        Return a created shipping address instance, created using
        the data returned by PayPal.
        """
        # Determine names - PayPal uses a single field
        ship_to_name = self.txn.value('SHIPTONAME')
        first_name = last_name = None
        parts = ship_to_name.split()
        if len(parts) == 1:
            last_name = ship_to_name
        elif len(parts) > 1:
            first_name = parts[0]
            last_name = " ".join(parts[1:])

        return ShippingAddress.objects.create(
            first_name=first_name,
            last_name=last_name,
            line1=self.txn.value('SHIPTOSTREET'),
            line4=self.txn.value('SHIPTOCITY'),
            state=self.txn.value('SHIPTOSTATE'),
            postcode=self.txn.value('SHIPTOZIP'),
            country=Country.objects.get(iso_3166_1_a2=self.txn.value('COUNTRYCODE'))
        )
