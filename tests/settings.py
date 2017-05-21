from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR
from oscar.defaults import *


# To specify integration settings (which include passwords, hence why they
# are not committed), create an integration.py module.
try:
    from integration import *
except ImportError:
    PAYPAL_API_USERNAME = ''
    PAYPAL_API_PASSWORD = ''
    PAYPAL_API_SIGNATURE = ''
    PAYPAL_PAYFLOW_VENDOR_ID = ''
    PAYPAL_PAYFLOW_PASSWORD = ''

SECRET_KEY = '9%d9&5!^+hcq!pin#0lfz(qj8j2h7y$p*rr-o#cy+)9%dyvwkn'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'paypal',
    'compressor',
] + get_core_apps([
    'tests.shipping',
])
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    # Oscar specific
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.core.context_processors.metadata',
    'oscar.apps.customer.notifications.context_processors.notifications',
)
DEBUG = False
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}
TEMPLATE_DIRS = (OSCAR_MAIN_TEMPLATE_DIR,)
SITE_ID = 1
ROOT_URLCONF = 'tests.urls'
COMPRESS_ENABLED = False
STATIC_URL = '/'
STATIC_ROOT = '/static/'
NOSE_ARGS = ['-s', '--with-spec']
# Oscar 1.0 factories assume this setting is present. Fixed in 1.1.
OSCAR_INITIAL_ORDER_STATUS = 'A'
