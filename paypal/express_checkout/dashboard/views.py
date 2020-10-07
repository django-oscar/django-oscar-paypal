from django.views import generic

from paypal.express_checkout import models


class TransactionListView(generic.ListView):
    model = models.ExpressCheckoutTransaction
    template_name = 'paypal/express_checkout/dashboard/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(generic.DetailView):
    model = models.ExpressCheckoutTransaction
    template_name = 'paypal/express_checkout/dashboard/transaction_detail.html'
    context_object_name = 'txn'
