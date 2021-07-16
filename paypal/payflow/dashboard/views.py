from django import http
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import generic

from paypal.payflow import facade, models


class TransactionListView(generic.ListView):
    model = models.PayflowTransaction
    template_name = 'paypal/payflow/dashboard/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(generic.DetailView):
    model = models.PayflowTransaction
    template_name = 'paypal/payflow/dashboard/transaction_detail.html'
    context_object_name = 'txn'

    def get_context_data(self, **kwargs):
        ctx = super(TransactionDetailView, self).get_context_data(**kwargs)
        ctx['show_form_buttons'] = getattr(
            settings, 'PAYPAL_PAYFLOW_DASHBOARD_FORMS', False)
        return ctx

    def post(self, request, *args, **kwargs):
        orig_txn = self.get_object()
        if not getattr(settings, 'PAYPAL_PAYFLOW_DASHBOARD_FORMS', False):
            messages.error(self.request, _("Dashboard actions not permitted"))
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=orig_txn.id)
        dispatch_map = {
            'credit': self.credit,
            'void': self.void,
            'capture': self.capture,
        }
        action = request.POST.get('action', None)
        if action in dispatch_map:
            return dispatch_map[action](orig_txn)
        return http.HttpBadRequest("Unrecognised action")

    def capture(self, orig_txn):
        try:
            txn = facade.delayed_capture(orig_txn.comment1)
        except Exception as e:
            messages.error(
                self.request, _("Unable to settle transaction - %s") % e)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=orig_txn.id)
        else:
            messages.success(
                self.request, _("Transaction %s settled") % orig_txn.pnref)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=txn.id)

    def credit(self, orig_txn):
        try:
            txn = facade.credit(orig_txn.comment1)
        except Exception as e:
            messages.error(self.request, _("Unable to credit transaction - %s") % e)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=orig_txn.id)
        else:
            messages.success(self.request, _("Transaction %s credited") % orig_txn.pnref)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=txn.id)

    def void(self, orig_txn):
        try:
            txn = facade.void(orig_txn.comment1, orig_txn.pnref)
        except Exception as e:
            messages.error(self.request, _("Unable to void transaction - %s") % e)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=orig_txn.id)
        else:
            messages.success(self.request, _("Transaction %s voided") % orig_txn.pnref)
            return redirect('payflow_dashboard:paypal-payflow-detail', pk=txn.id)
