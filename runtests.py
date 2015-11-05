#!/usr/bin/env python
import sys
from coverage import coverage
from optparse import OptionParser

from django.conf import settings

if not settings.configured:
    extra_settings = {
        'PAYPAL_EXPRESS_URL': 'https://www.sandbox.paypal.com/webscr',
        'PAYPAL_SANDBOX_MODE': True,
        'PAYPAL_VERSION': '88.0',
        'PAYPAL_PAYFLOW_TEST_MODE': True,
    }
    # To specify integration settings (which include passwords, hence why they
    # are not committed), create an integration.py module.
    try:
        from integration import *
    except ImportError:
        extra_settings.update({
            'PAYPAL_API_USERNAME': '',
            'PAYPAL_API_PASSWORD': '',
            'PAYPAL_API_SIGNATURE': '',
            'PAYPAL_PAYFLOW_VENDOR_ID': '',
            'PAYPAL_PAYFLOW_PASSWORD': '',
        })
    else:
        for key, value in list(locals().items()):
            if key.startswith('PAYPAL'):
                extra_settings[key] = value

    from oscar.defaults import *
    for key, value in list(locals().items()):
        if key.startswith('OSCAR'):
            extra_settings[key] = value
    extra_settings['OSCAR_ALLOW_ANON_CHECKOUT'] = True

    from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR

    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
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
        ]),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'oscar.apps.basket.middleware.BasketMiddleware',
        ),
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
        ),
        DEBUG=False,
        HAYSTACK_CONNECTIONS={
            'default': {
                'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
            },
        },
        TEMPLATE_DIRS=(OSCAR_MAIN_TEMPLATE_DIR,),
        SITE_ID=1,
        ROOT_URLCONF='tests.urls',
        COMPRESS_ENABLED=False,
        STATIC_URL='/',
        STATIC_ROOT='/static/',
        NOSE_ARGS=['-s', '--with-spec'],
        # Oscar 1.0 factories assume this setting is present. Fixed in 1.1.
        OSCAR_INITIAL_ORDER_STATUS='A',
        **extra_settings
    )

from django_nose import NoseTestSuiteRunner


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    c = coverage(source=['paypal'], omit=['*migrations*', '*tests*'],
                 auto_data=True)
    c.start()
    num_failures = test_runner.run_tests(test_args)
    c.stop()

    if num_failures > 0:
        sys.exit(num_failures)
    print("Generating HTML coverage report")
    c.html_report()


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    run_tests(*args)
