from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns

from oscar.app import application
from paypal.express.urls import base_patterns, buyer_pays_on_website_patterns, buyer_pays_on_paypal_patterns

urlpatterns = patterns(
    '',
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
urlpatterns += i18n_patterns(
    '',
    (r'^checkout/paypal/', include(base_patterns)),
    (r'^checkout/paypal/option-paypal/', include(buyer_pays_on_paypal_patterns)),
    (r'^checkout/paypal/option-website/', include(buyer_pays_on_website_patterns)),
    (r'', include(application.urls)),
)
