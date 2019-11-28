from django.apps import apps
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    # PayPal Express integration...
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    # Dashboard views for Payflow Pro
    url(r'^dashboard/paypal/payflow/', apps.get_app_config("payflow_dashboard").urls),
    # Dashboard views for Express
    url(r'^dashboard/paypal/express/', apps.get_app_config("express_dashboard").urls),
    url(r'^', include(apps.get_app_config('oscar').urls[0])),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
