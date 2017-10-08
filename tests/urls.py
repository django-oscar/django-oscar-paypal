from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from oscar.app import application

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    url(r'', include(application.urls)),
)
