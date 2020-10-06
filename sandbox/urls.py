from django.apps import apps
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import include, path


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    # PayPal Express integration...
    path('checkout/paypal/', include('paypal.express_checkout.urls')),
    # Dashboard views for Payflow Pro
    path('dashboard/paypal/payflow/', apps.get_app_config("payflow_dashboard").urls),
    # Dashboard views for Express
    path('dashboard/paypal/express/', apps.get_app_config("express_dashboard").urls),
    # Dashboard views for Express Checkout
    path('dashboard/paypal/express-checkout/', apps.get_app_config('express_checkout_dashboard').urls),
    path('', include(apps.get_app_config('oscar').urls[0])),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
