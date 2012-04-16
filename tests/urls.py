from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^checkout/paypal/', include('paypal.express.urls')),
)