from django.conf.urls.defaults import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from paypal.adaptive.dashboard import views


class AdaptiveDashboardApplication(Application):
    name = None
    list_view = views.TransactionListView
    detail_view = views.TransactionDetailView
    payment_details_view = views.PaymentDetailsView

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^transactions/$', self.list_view.as_view(),
                name='paypal-adaptive-list'),
            url(r'^transactions/(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='paypal-adaptive-detail'),
            url(r'^transactions/details/(?P<pay_key>.+)/$',
                self.payment_details_view.as_view(),
                name='paypal-adaptive-payment-details'),
        )
        return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required


application = AdaptiveDashboardApplication()
