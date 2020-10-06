from django.apps import apps
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from paypal.express.urls import base_patterns, buyer_pays_on_paypal_patterns, buyer_pays_on_website_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    path('checkout/paypal/', include(base_patterns)),
    path('checkout/paypal/option-paypal/', include(buyer_pays_on_paypal_patterns)),
    path('checkout/paypal/option-website/', include(buyer_pays_on_website_patterns)),
    path('', include(apps.get_app_config("oscar").urls[0])),
)
