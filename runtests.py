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
        })
    else:
        for key, value in locals().items():
            if key.startswith('PAYPAL'):
                extra_settings[key] = value

    from oscar.defaults import *
    for key, value in locals().items():
        if key.startswith('OSCAR'):
            extra_settings[key] = value
    extra_settings['OSCAR_ALLOW_ANON_CHECKOUT'] = True

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
                'oscar',
                'oscar.apps.checkout',
                'oscar.apps.partner',
                'oscar.apps.customer',
                'oscar.apps.shipping',
                'oscar.apps.offer',
                'oscar.apps.catalogue',
                'oscar.apps.catalogue.reviews',
                'oscar.apps.payment',
                'oscar.apps.promotions',
                'oscar.apps.voucher',
                'oscar.apps.basket',
                'oscar.apps.order',
                'oscar.apps.address',
                'oscar.apps.analytics',
                'oscar.apps.dashboard.reports',
                'oscar.apps.dashboard.catalogue',
                'oscar.apps.dashboard.orders',
                'oscar.apps.dashboard.orders',
                'oscar.apps.dashboard.offers',
                'oscar.apps.dashboard.ranges',
                'oscar.apps.dashboard.vouchers',
                'oscar.apps.dashboard.promotions',
                'sorl.thumbnail',
                'paypal',
                'south',
                ],
            MIDDLEWARE_CLASSES=(
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.transaction.TransactionMiddleware',
                'oscar.apps.basket.middleware.BasketMiddleware',
            ),
            DEBUG=False,
            SOUTH_TESTS_MIGRATE=False,
            HAYSTACK_SITECONF='oscar.search_sites',
            HAYSTACK_SEARCH_ENGINE='dummy',
            SITE_ID=1,
            ROOT_URLCONF='tests.urls',
            NOSE_ARGS=['-s'],
            **extra_settings
        )

from django_nose import NoseTestSuiteRunner


def run_tests(*test_args):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=2)

    c = coverage(source=['paypal'], omit=['*migrations*', '*tests*'])
    c.start()
    num_failures = test_runner.run_tests(test_args)
    c.stop()

    if num_failures > 0:
        sys.exit(num_failures)
    print "Generating HTML coverage report"
    c.html_report()

def generate_migration():
    from south.management.commands.schemamigration import Command
    com = Command()
    com.handle(app='paypal', initial=True)


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    run_tests(*args)
