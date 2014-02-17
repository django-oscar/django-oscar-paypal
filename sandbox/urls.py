from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.app import application
from paypal.payflow.app import application as payflow
from paypal.express.dashboard.app import application as express_dashboard
from paypal.adaptive.dashboard.app import application as adaptive_dashboard

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    # PayPal Express integration...
    (r'^checkout/paypal/', include('paypal.express.urls')),
    # Dashboard views for Payflow Pro
    (r'^dashboard/paypal/payflow/', include(payflow.urls)),
    # Dashboard views for Express
    (r'^dashboard/paypal/express/', include(express_dashboard.urls)),
    # Dashboard views for Adaptive
    (r'^dashboard/paypal/adaptive/', include(adaptive_dashboard.urls)),
    (r'', include(application.urls)),
)
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += patterns('',
        url(r'^404$', TemplateView.as_view(template_name='404.html')),
        url(r'^500$', TemplateView.as_view(template_name='500.html')),
    )
