===============================
PayPal package for django-oscar
===============================

.. warning::

    This is a work in progress - not ready for production yet.

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

First, you'll need to create a 

Fetch package (not ready just yet)::

    pip install django-oscar-paypal

Add following settings for which you'll need to create a sandbox account with
PayPal::

    PAYPAL_API_USERNAME = 'test_xxxx.gmail.com'
    PAYPAL_API_PASSWORD = '123456789'
    PAYPAL_API_SIGNATURE = '...'

Augment your ``INSTALLED_APPS`` to include ``paypal.express``.

Settings
--------

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

Not included (yet)
------------------

The following options are part of the PayPal Express API but are not handled
within this implementation - mainly as there's not obvious how you can handle
these in a 'generic' way within oscar:

* Gift wrapping
* Buyer consent to receive promotional emails
* Survey questions
* Not using shipping address from PayPal
* Shipping address overrides
* User confirming order on PayPal (bypassing review stage)
* Instant update API (for dynamically setting shipping methods based on entered
  address on PayPal's side)

Known issues (eg. to-do list)
-----------------------------

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

Use the Github issue tracker for any problems.


