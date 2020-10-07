from django.utils.translation import gettext_lazy as _
from django.urls import path

from oscar.core.application import OscarDashboardConfig


class ExpressDashboardApplication(OscarDashboardConfig):
    name = "paypal.express.dashboard"
    label = "express_dashboard"
    namespace = "express_dashboard"
    verbose_name = _("Express dashboard")

    default_permissions = ["is_staff"]

    def ready(self):
        from . import views
        self.list_view = views.TransactionListView
        self.detail_view = views.TransactionDetailView

    def get_urls(self):
        urlpatterns = [
            path('transactions/', self.list_view.as_view(),
                 name='paypal-express-list'),
            path('transactions/<int:pk>/', self.detail_view.as_view(),
                 name='paypal-express-detail'),
        ]
        return self.post_process_urls(urlpatterns)
