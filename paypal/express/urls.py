from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from paypal.express import views

urlpatterns = [
    # Views for normal flow that starts on the basket page
    url(r'^redirect/', views.RedirectView.as_view(), name='paypal-redirect'),
    url(r'^preview/(?P<basket_id>\d+)/$',
        views.SuccessResponseView.as_view(preview=True),
        name='paypal-success-response'),
    url(r'^cancel/(?P<basket_id>\d+)/$', views.CancelResponseView.as_view(),
        name='paypal-cancel-response'),
    url(r'^place-order/(?P<basket_id>\d+)/$', views.SuccessResponseView.as_view(),
        name='paypal-place-order'),
    # Callback for getting shipping options for a specific basket
    url(r'^shipping-options/(?P<basket_id>\d+)/(?P<country_code>\w+)?',
        csrf_exempt(views.ShippingOptionsView.as_view()),
        name='paypal-shipping-options'),
    # View for using PayPal as a payment method
    url(r'^payment/', views.RedirectView.as_view(as_payment_method=True),
        name='paypal-direct-payment'),
]
