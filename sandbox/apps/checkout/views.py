from decimal import Decimal as D

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.apps.checkout import views
from oscar.apps.payment import forms
from oscar.apps.payment import exceptions

from paypal.payflow import facade
from paypal.adaptive import gateway
from paypal import utils


class PaymentDetailsView(views.PaymentDetailsView):

    def get_context_data(self, **kwargs):
        # Override method so the bankcard and billing address forms can be added
        # to the context.
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', forms.BankcardForm())
        ctx['billing_address_form'] = kwargs.get('billing_address_form',
                                                 forms.BillingAddressForm())
        return ctx

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard/billingaddress submission. If
        # it is valid, we render the preview screen with the forms hidden within
        # it.  When the preview is submitted, we pick up the 'action' parameters
        # and actually place the order.
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = forms.BillingAddressForm(request.POST)
        if not all([bankcard_form.is_valid(), billing_address_form.is_valid()]):
            # Form validation failed, render page again with errors
            self.preview = False
            ctx = self.get_context_data(bankcard_form=bankcard_form,
                                        billing_address_form=billing_address_form)
            return self.render_to_response(ctx)

        # Render preview with bankcard and billing address details hidden
        return self.render_preview(request,
                                   bankcard_form=bankcard_form,
                                   billing_address_form=billing_address_form)

    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = forms.BillingAddressForm(request.POST)
        if not all([bankcard_form.is_valid(), billing_address_form.is_valid()]):
            messages.error(request, "Invalid submission")
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        bankcard = bankcard_form.get_bankcard_obj()

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        return self.submit(
            request.basket,
            payment_kwargs={'bankcard': bankcard,
                            'billing_address': billing_address_form.cleaned_data})

    def handle_payment(self, order_number, total_incl_tax, **kwargs):
        # Make submission to PayPal.
        try:
            # Using authorization here (two-stage model).  You could use sale to
            # perform the auth and capture in one step.  The choice is dependent
            # on your business model.
            facade.authorize(order_number,
                             total_incl_tax,
                             kwargs['bankcard'],
                             kwargs['billing_address'])
        except facade.NotApproved, e:
            # Submission failed
            raise exceptions.UnableToTakePayment(e.message)


class AdaptivePaymentsView(generic.RedirectView):
    permanent = False

    def transaction(self):
        # This is just a dummy chained transaction set up to test the end to
        # end process.  It doesn't actually use the submitted basket at all but
        # hard-codes some test users from a PayPal sandbox account.
        receivers = (
            gateway.Receiver(email='david._1332854868_per@gmail.com',
                            amount=D('12.00'), is_primary=True),
            gateway.Receiver(email='david._1359545821_pre@gmail.com',
                            amount=D('12.00'), is_primary=False),
        )
        return_url = utils.absolute_url(
            self.request, reverse('checkout:adaptive-payments-success'))
        cancel_url = utils.absolute_url(
            self.request, reverse('checkout:adaptive-payments-cancel'))
        return gateway.pay(
            receivers=receivers,
            currency=settings.PAYPAL_CURRENCY,
            return_url=return_url,
            cancel_url=cancel_url,
            ip_address=self.request.META['REMOTE_ADDR'])

    def get_redirect_url(self, **kwargs):
        txn = self.transaction()
        if not txn.is_successful:
            messages.error(
                self.request,
                _("An error occurred communicating with PayPal"))
            url = '.'
        else:
            url = txn.redirect_url
        return url


class SuccessResponseView(generic.TemplateView):
    pass


class CancelResponseView(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        messages.error(self.request, _("PayPal transaction cancelled"))
        return reverse('checkout:payment-details')
