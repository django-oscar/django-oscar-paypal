.. django-oscar-paypal documentation master file, created by
   sphinx-quickstart on Wed Aug 22 20:12:56 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-oscar-paypal's documentation!
===============================================

This package provides integration between django-oscar and two of PayPal's
payment options:

* PayPal Express -

* PayPal PayFlow Pro -

It's possible to use both of these options individually or at the same time.

Installation
------------

Install::

    pip install django-oscar-paypal

add ``paypal`` to your ``INSTALLED_APPS``, and run::

    python manage.py syncdb

Sandbox
-------

This is a sandbox build within the project that demonstrates an integration
between oscar and payflow pro.  It includes both PayPal Express and PayFlow Pro.

Contents:

.. toctree::
    :maxdepth: 2

    express
    payflow


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
