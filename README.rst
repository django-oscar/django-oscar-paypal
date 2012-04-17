===============================
PayPal package for django-oscar
===============================

This is a work in progress...

Installation
============

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
