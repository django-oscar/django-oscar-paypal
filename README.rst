===============================
PayPal package for django-oscar
===============================

This is a work in progress - not ready for production yet.  It also depends on
the forthcoming version of oscar (0.2) which hasn't been released yet.

Overview
========

`PayPal Express` is an API for integrating PayPal payments into an ecommerce
site.  A typical implementation involves redirecting the user to PayPal's site
where they enter their shipping and billing information before arriving back on
the merchant site to confirm the order.

This library provides integration between PayPal Express and `django-oscar`_.

See the `PDF documentation`_ for the gory details.

.. _`PayPal Express`: https://www.paypal.com/uk/cgi-bin/webscr?cmd=_additional-payment-ref-impl1
.. _`PDF documentation`: https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_ExpressCheckout_IntegrationGuide.pdf
.. _`django-oscar`: https://github.com/tangentlabs/django-oscar

Installation
============

First, you'll need to create a sandbox merchant account with PayPal - this will
provide a username, password and 'signature' which are used to authenticate API
requests.

If you want to test your installation in a browser (which you should), then
you'll need to also create a sandbox buyer account so you can checkout.

Fetch package (not ready just yet)::

    pip install django-oscar-paypal

Add following settings using the details from your sandbox buyer account::

    PAYPAL_API_USERNAME = 'test_xxxx.gmail.com'
    PAYPAL_API_PASSWORD = '123456789'
    PAYPAL_API_SIGNATURE = '...'

Augment your ``INSTALLED_APPS`` to include ``paypal.express`` and run syncdb to
create the appropriate models.

Next, you need to add the PayPal URLs to your URL config.  This can be done as
follows::

    from django.contrib import admin
    from oscar.app import shop

    urlpatterns = patterns('',
        (r'^admin/', include(admin.site.urls)),
        (r'^checkout/paypal/', include('paypal.express.urls')),
        (r'', include(shop.urls)),

Finally, you need to modify oscar's basket template to include the button that
links to PayPal.  This can be done by creating a new template
``templates/basket/basket.html`` with content::

    {% extends 'templates/basket/basket.html' %}

    {% block formactions %}
    <div class="form-actions">
        <a href="{% url paypal-redirect %}"><img src="https://www.paypal.com/en_US/i/btn/btn_xpressCheckout.gif" align="left" style="margin-right:7px;"></a>
        <a href="{% url checkout:index %}" class="pull-right btn btn-large btn-primary">Proceed to checkout</a>
    </div>
    {% endblock %}

Note that we extending the ``basket/basket.html`` template from oscar and
overriding the ``formactions`` block.  For this trick to work, you need to
ensure that you have ``OSCAR_PARENT_TEMPLATE_DIR`` in your ``TEMPLATE_DIRS``
setting::

    import os
    location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)
    from oscar import OSCAR_PARENT_TEMPLATE_DIR
    TEMPLATE_DIRS = (
        location('templates'),
        os.path.join(OSCAR_PARENT_TEMPLATE_DIR, 'templates'),
        OSCAR_PARENT_TEMPLATE_DIR,
    )

If anything is unclear or not workin as expected then review how the 'sandbox`
installation is set-up.  This is a working oscar install that uses PayPal
Express.

Settings
--------

There's a smorgasboard of options that can be used, as there's many ways to
customised the Express Checkout experience.  Most of these are handled by simple
settings.

* ``PAYPAL_SANDBOX_MODE`` - whether to use PayPal's sandbox.  Defaults to ``True``.
* ``PAYPAL_CURRENCY`` - the currency to use for transactions.  Defaults to ``GBP``.
* ``PAYPAL_API_VERSION`` - the version of API used (defaults to ``60.0``)
* ``PAYPAL_ALLOW_NOTE`` - whether to allow the customer to enter a note (defaults to ``True``)
* ``PAYPAL_CUSTOMER_SERVICES_NUMBER`` - customer services number to display on
  the PayPal review page.
* ``PAYPAL_HEADER_IMG`` - the absolute path to a header image 
* ``PAYPAL_HEADER_BACK_COLOR`` - background color (6-char hex value) for header
  background
* ``PAYPAL_HEADER_BORDER_COLOR`` - background color (6-char hex value) for header border
* ``PAYPAL_CALLBACK_TIMEOUT`` - timeout in seconds for the instant update
  callback

Not included
------------

The following options are part of the PayPal Express API but are not handled
within this implementation - mainly as it's not obvious how you can handle
these in a 'generic' way within oscar:

* Gift wrapping
* Buyer consent to receive promotional emails
* Survey questions
* User confirming order on PayPal (bypassing review stage)
* Recurring payments

Known issues
------------

* Hasn't been adapted to work with offers and vouchers (yet).  The discounts are
  not passed to PayPal at the moment.

* Vouchers may have expired during the time when the user is on the PayPal site.

Contribute
==========

Do this::

    mkvirtualenv oscar-paypal
    git clone git://github.com/tangentlabs/django-oscar-paypal.git
    cd django-oscar-paypal
    pip install -r requirements.txt

then you should be able to run the tests using::

    ./run_tests.sh

There is also a sandbox site for exploring a sample oscar site.  Set it up::

    cd sandbox
    ./manage.py syncdb --noinput
    ./manage.py migrate
    ./manage.py oscar_import_catalogue data/books-catalogue.csv

and run it::

    ./manage.py runserver

Use the `Github issue tracker`_ for any problems.

.. _`Github issue tracker`: https://github.com/tangentlabs/django-oscar-paypal/issues

