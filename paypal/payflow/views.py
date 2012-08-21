from django.views import generic

from paypal.payflow import models


class TransactionListView(generic.ListView):
    model = models.PayflowTransaction
    template_name = 'paypal/payflow/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(generic.DetailView):
    model = models.PayflowTransaction
    template_name = 'paypal/payflow/transaction_detail.html'
    context_object_name = 'txn'
