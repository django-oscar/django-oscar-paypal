from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from oscar.apps.checkout import views
from oscar.apps.payment.forms import BankcardForm
from oscar.apps.payment import exceptions

from paypal.payflow import facade


class PaymentDetailsView(views.PaymentDetailsView):

    def get_context_data(self, **kwargs):
        # Override so the bankcard form can be added to the context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
        return ctx

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard submission. If it is valid,
        # we render the preview screen with the bankcard form hidden within it.
        # When the preview is submitted, we pick up the 'action' paramters and
        # actually place the order.
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        bankcard_form = BankcardForm(request.POST)
        if not bankcard_form.is_valid():
            self.preview = False
            ctx = self.get_context_data(bankcard_form=bankcard_form)
            return self.render_to_response(ctx)

        # Render preview with bankcard details hidden
        return self.render_preview(request, bankcard_form=bankcard_form)

    def do_place_order(self, request):
        # Helper method to check that the hidden bankcard form wasn't tinkered
        # with
        bankcard_form = BankcardForm(request.POST)
        if not bankcard_form.is_valid():
            messages.error(request, "Invalid submission")
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        bankcard = bankcard_form.get_bankcard_obj()

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method.
        return self.submit(request.basket,
                           payment_kwargs={'bankcard': bankcard})

    def handle_payment(self, order_number, total_incl_tax, **kwargs):
        # Make submission to PayPal.
        try:
            facade.authorize(order_number,
                            kwargs['bankcard'],
                            total_incl_tax)
        except facade.NotApproved, e:
            # Submission failed
            raise exceptions.UnableToTakePayment(e.message)
