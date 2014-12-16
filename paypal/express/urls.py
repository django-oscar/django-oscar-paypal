from django.conf import settings
from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt

from paypal.express import views
from paypal.express.gateway import buyer_pays_on_paypal

# we need all urls enabled during tests
_TEST_ENVIRONMENT = getattr(settings, 'TEST_ENVIRONMENT', False)


urlpatterns = patterns('',
    # Views for normal flow that starts on the basket page
    url(r'^redirect/', views.RedirectView.as_view(), name='paypal-redirect'),
    url(r'^cancel/(?P<basket_id>\d+)/$', views.CancelResponseView.as_view(),
        name='paypal-cancel-response'),
    # Callback for getting shipping options for a specific basket
    url(r'^shipping-options/(?P<basket_id>\d+)/',
        csrf_exempt(views.ShippingOptionsView.as_view()),
        name='paypal-shipping-options'),
    # View for using PayPal as a payment method
    url(r'^payment/', views.RedirectView.as_view(as_payment_method=True),
        name='paypal-direct-payment'),
)


if buyer_pays_on_paypal() or _TEST_ENVIRONMENT:
    urlpatterns += patterns(
        '',
        url(r'^handle-order/(?P<basket_id>\d+)/$',
            views.SuccessResponseView.as_view(preview=True),
            name='paypal-handle-order'),
    )

if not buyer_pays_on_paypal() or _TEST_ENVIRONMENT:
    urlpatterns += patterns(
        '',
        url(r'^place-order/(?P<basket_id>\d+)/$', views.SuccessResponseView.as_view(),
            name='paypal-place-order'),
        url(r'^preview/(?P<basket_id>\d+)/$',
            views.SuccessResponseView.as_view(preview=True),
            name='paypal-success-response'),
    )
