from django.conf.urls.defaults import *

from paypal.express import views


urlpatterns = patterns('',
    # Views for normal flow that starts on the basket page
    url(r'^redirect/', views.RedirectView.as_view(), name='paypal-redirect'),
    url(r'^preview/', views.SuccessResponseView.as_view(preview=True),
        name='paypal-success-response'),
    url(r'^cancel/', views.CancelResponseView.as_view(),
        name='paypal-cancel-response'),
    url(r'^place-order/', views.SuccessResponseView.as_view(),
        name='paypal-place-order'),
    # Callback for getting shipping options for a specific basket
    url(r'^shipping-options/(?P<basket_id>\d+)/', views.ShippingOptionsView.as_view(),
        name='paypal-shipping-options'),
    # View for using PayPal as a payment method
    url(r'^payment/', views.RedirectView.as_view(as_payment_method=True),
        name='paypal-direct-payment'),
)
