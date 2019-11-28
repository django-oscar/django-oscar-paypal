from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from oscar.core.application import OscarDashboardConfig


class PayFlowDashboardApplication(OscarDashboardConfig):
    name = "paypal.payflow.dashboard"
    label = "payflow_dashboard"
    namespace = "payflow_dashboard"
    verbose_name = _("Payflow dashboard")

    default_permissions = ["is_staff"]

    def ready(self):
        from . import views
        self.list_view = views.TransactionListView
        self.detail_view = views.TransactionDetailView

    def get_urls(self):
        urlpatterns = [
            url(r'^transactions/$', self.list_view.as_view(),
                name='paypal-payflow-list'),
            url(r'^transactions/(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='paypal-payflow-detail'),
        ]
        return self.post_process_urls(urlpatterns)
