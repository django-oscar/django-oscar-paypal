from django.views import generic
from django.core.urlresolvers import reverse

from paypal.adaptive import models, gateway


class TransactionListView(generic.ListView):
    model = models.AdaptiveTransaction
    template_name = 'paypal/adaptive/dashboard/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(generic.DetailView):
    model = models.AdaptiveTransaction
    template_name = 'paypal/adaptive/dashboard/transaction_detail.html'
    context_object_name = 'txn'


class PaymentDetailsView(generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        txn = gateway.details(kwargs['pay_key'])
        return reverse('paypal-adaptive-detail', kwargs={'pk': txn.id})
