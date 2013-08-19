from django.views import generic

from paypal.adaptive import models


class TransactionListView(generic.ListView):
    model = models.AdaptiveTransaction
    template_name = 'paypal/adaptive/dashboard/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(generic.DetailView):
    model = models.AdaptiveTransaction
    template_name = 'paypal/adaptive/dashboard/transaction_detail.html'
    context_object_name = 'txn'
