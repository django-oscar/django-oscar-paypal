from django.apps import apps
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns

from paypal.express.urls import base_patterns, buyer_pays_on_paypal_patterns, buyer_pays_on_website_patterns

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    url(r'^checkout/paypal/', include(base_patterns)),
    url(r'^checkout/paypal/option-paypal/', include(buyer_pays_on_paypal_patterns)),
    url(r'^checkout/paypal/option-website/', include(buyer_pays_on_website_patterns)),
    url(r'^', include(apps.get_app_config("oscar").urls[0])),
)
