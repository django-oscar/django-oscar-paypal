from django.contrib import messages
from django.shortcuts import redirect
from oscar.apps.checkout import views
from oscar.apps.payment import forms, models

from paypal.payflow import facade


class PaymentDetailsView(views.PaymentDetailsView):
    """
    An example view that shows how to integrate BOTH PayPal Express
    (see `get_context_data method`) and PayPal Flow (the other methods).
    Naturally, you will only want to use one of the two.
    """
    template_name = 'checkout/payment_details.html'
    template_name_preview = 'checkout/preview.html'

    def get_context_data(self, **kwargs):
        """
        Add data for Paypal Express flow.
        """
        # Override method so the bankcard and billing address forms can be
        # added to the context.
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get(
            'bankcard_form', forms.BankcardForm())
        ctx['billing_address_form'] = kwargs.get(
            'billing_address_form', forms.BillingAddressForm())
        return ctx

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard/billing_address submission.
        # If it is valid, we render the preview screen with the forms hidden
        # within it.  When the preview is submitted, we pick up the 'action'
        # parameters and actually place the order.
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = forms.BillingAddressForm(request.POST)
        if not all([bankcard_form.is_valid(),
                    billing_address_form.is_valid()]):
            # Form validation failed, render page again with errors
            self.preview = False
            ctx = self.get_context_data(
                bankcard_form=bankcard_form,
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
        if not all([bankcard_form.is_valid(),
                    billing_address_form.is_valid()]):
            messages.error(request, "Invalid submission")
            return redirect('checkout:payment-details')

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        submission = self.build_submission()
        submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
        submission['payment_kwargs']['billing_address'] = billing_address_form.cleaned_data
        return self.submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        """
        Make submission to PayPal
        """
        # Using authorization here (two-stage model).  You could use sale to
        # perform the auth and capture in one step.  The choice is dependent
        # on your business model.
        facade.authorize(
            order_number, total.incl_tax,
            kwargs['bankcard'], kwargs['billing_address'])

        # Record payment source and event
        source_type, is_created = models.SourceType.objects.get_or_create(
            name='PayPal')
        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax, currency=total.currency)
        self.add_payment_source(source)
        self.add_payment_event('Authorised', total.incl_tax)
