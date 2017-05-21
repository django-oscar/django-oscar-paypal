import django
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from paypal.express.dashboard import views


class ExpressDashboardApplication(Application):
    name = None
    list_view = views.TransactionListView
    detail_view = views.TransactionDetailView

    def get_urls(self):
        urlpatterns = [
            url(r'^transactions/$', self.list_view.as_view(),
                name='paypal-express-list'),
            url(r'^transactions/(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='paypal-express-detail'),
        ]
        if django.VERSION[:2] < (1, 8):
            from django.conf.urls import patterns

            urlpatterns = patterns('', *urlpatterns)
        return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required


application = ExpressDashboardApplication()

