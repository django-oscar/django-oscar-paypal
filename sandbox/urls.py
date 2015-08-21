from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from apps.app import application
from paypal.payflow.dashboard.app import application as payflow
from paypal.express.dashboard.app import application as express_dashboard

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
urlpatterns += i18n_patterns('',
    # PayPal Express integration...
    (r'^checkout/paypal/', include('paypal.express.urls')),
    # Dashboard views for Payflow Pro
    (r'^dashboard/paypal/payflow/', include(payflow.urls)),
    # Dashboard views for Express
    (r'^dashboard/paypal/express/', include(express_dashboard.urls)),
    (r'', include(application.urls)),
)
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
