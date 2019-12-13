from django.apps import apps
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    url(r'^', include(apps.get_app_config("oscar").urls[0])),
)
