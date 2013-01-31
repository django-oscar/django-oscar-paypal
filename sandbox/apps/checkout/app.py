from django.conf.urls import patterns, url
from oscar.apps.checkout import app

from apps.checkout import views


class CheckoutApplication(app.CheckoutApplication):
    payment_details_view = views.PaymentDetailsView

    def get_urls(self):
        urls = super(CheckoutApplication, self).get_urls()
        urls += patterns('',
            url(r'adaptive-payments/$', views.AdaptivePaymentsView.as_view(),
                name='adaptive-payments'),
            url(r'adaptive-payments/success/$', views.SuccessResponseView.as_view(),
                name='adaptive-payments-success'),
            url(r'adaptive-payments/cancel/$', views.CancelResponseView.as_view(),
                name='adaptive-payments-cancel')
        )
        return urls


application = CheckoutApplication()
