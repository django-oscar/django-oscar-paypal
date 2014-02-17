from django.conf.urls.defaults import *

from oscar.app import shop

urlpatterns = patterns('',
    (r'^checkout/paypal/', include('paypal.express.urls')),
    (r'', include(shop.urls)),
)