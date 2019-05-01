.. django-oscar-paypal documentation master file, created by
   sphinx-quickstart on Wed Aug 22 20:12:56 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-oscar-paypal's documentation!
===============================================

This package provides integration between django-oscar and two of PayPal's
payment options:

* *PayPal Express* - Involves redirecting customer's over to PayPal's site where
  they can choose shipping options and confirm payment using their PayPal
  account.  The customer is then redirected back to the merchant site where they
  confirm the order.

* *PayPal PayFlow Pro* - Allows you to accept customer payments on your site
  without requiring a redirect to PayPal.  This allows the customer to pay with
  a normal bankcard rather than their PayPal account.

It's possible to use both of these options individually or at the same time.
Further, it's possible to use either without Oscar.

Installation
------------

Whichever payment option you wish to use, the package installation instructions
are the same.

Install::

    pip install django-oscar-paypal

By default, this won't install Oscar as well. To install Oscar, run::

    pip install "django-oscar-paypal[oscar]"

Finally, add ``paypal`` to your ``INSTALLED_APPS``, and run::

    python manage.py migrate


Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    express
    payflow
    contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
