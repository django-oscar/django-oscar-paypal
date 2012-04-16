=================================
PayPal package for django-oscar
=================================

This is a work in progress...

Requirements
============

Express checkout from basket page
Express checkout as payment method


Installation
============

Add following settings::

    PAYPAL_API_URL = ''
    ...

Settings
--------

* ``PAYPAL_CURRENCY`` - the default currency to use for transactions.
* ``PAYPAL_API_URL`` - the URL
* ``PAYPAL_API_VERSION`` - the version of API used (defaults to 60.0)


Notes
=====

Express checkout
----------------

Customer bypasses shipping address and goes straight to Express checkout from 
the basket page.

Supports pre-auth model

Gotchas:
- don't know who customer is until they return from paypal express - voucher may
  not be valid at that point (eg used, expired)
- can't validate country of shipping address until you hear back from PayPal
-

Getting set-up:
- Need a merchant account

test@gmail.com / 332777704
