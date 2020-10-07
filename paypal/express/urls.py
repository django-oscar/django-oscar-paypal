from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from paypal.express import views
from paypal.express.gateway import buyer_pays_on_paypal

base_patterns = [
    # Views for normal flow that starts on the basket page
    path('redirect/', views.RedirectView.as_view(), name='paypal-redirect'),
    path('cancel/<int:basket_id>/', views.CancelResponseView.as_view(),
         name='paypal-cancel-response'),
    # Callback for getting shipping options for a specific basket
    re_path(r'^shipping-options/(?P<basket_id>\d+)/(?P<country_code>\w+)?',
            csrf_exempt(views.ShippingOptionsView.as_view()),
            name='paypal-shipping-options'),
    # View for using PayPal as a payment method
    path('payment/', views.RedirectView.as_view(as_payment_method=True),
         name='paypal-direct-payment'),
]


buyer_pays_on_paypal_patterns = [
    path('handle-order/(<int:basket_id>/', views.SuccessResponseView.as_view(preview=True),
         name='paypal-handle-order'),
]

buyer_pays_on_website_patterns = [
    path('place-order/<int:basket_id>/', views.SuccessResponseView.as_view(), name='paypal-place-order'),
    path('preview/<int:basket_id>/', views.SuccessResponseView.as_view(preview=True), name='paypal-success-response'),
]


if buyer_pays_on_paypal():
    urlpatterns = base_patterns + buyer_pays_on_paypal_patterns
else:
    urlpatterns = base_patterns + buyer_pays_on_website_patterns
