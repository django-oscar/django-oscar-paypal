from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns

from oscar.app import application

urlpatterns = patterns(
    '',
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
urlpatterns += i18n_patterns(
    '',
    (r'^checkout/paypal/', include('paypal.express.urls')),
    (r'', include(application.urls)),
)
