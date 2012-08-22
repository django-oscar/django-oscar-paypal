===========
Payflow Pro
===========

Payflow Pro is a server-to-server payment option

Read more details on the PayPal site.

.. note::

    This version of the library was built using the PP_PayflowPro_Guide.pdf
    found in the docs/guides folder.  It is recommended that developers read
    this guide so that they are familiar with the overall structure.

---------------
Getting started
---------------

You'll need to set-up a merchant account for PayPay:
https://merchant.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=merchant/payment_gateway

https://manager.paypal.com/

Register a new acccount with PayPal.
Create a PayFlow pro account with PayPal - you will need a:

* Vendor ID
* User (often same as vendor ID)
* Password
* Partner ID (normally "PayPal")

--------
Settings
--------

Required settings:

``PAYPAL_PAYFLOW_VENDOR_ID``
    Your merchant login ID created when you registered the account with PayPal.
``PAYPAL_PAYFLOW_PASSWORD``
    Your merchant password.

Optional settings:

``PAYPAL_PAYFLOW_USER``
    The ID of the user authorised to process transations.  If you only have one
    user on the account, then this is the same as the VENDOR_ID and there is no
    need to specify it.
``PAYPAL_PAYFLOW_PARTNER``
    The ID provided by a PayPal reseller.  If you created your account directly
    with PayPal, then the value to use is ``"PayPal`` - this is the default.
``PAYPAL_PAYFLOW_PRODUCTION_MODE``
    Whether to use PayPal's production servers.  This defaults to ``False`` but
    should be set to ``True`` in production.
``PAYPAL_PAYFLOW_DASHBOARD_FORMS``
    Whether to show forms within the transaction detail page which allow
    transactions to be captured, voided or credited.  Defaults to ``False``.

------------
Not included
------------

* Recurring billing
* Account verification (TRXTYPE=A)
* Voice authorisation (TRXTYPE=F)
* SWIPE transactions (eg card present)
* Non-referenced credits (eg refunding to an arbitrary bankcard).  All refunds
  must correspond to a previously settled transaction.

Sign in here:
https://manager.paypal.com/

Server-to-server payment gateway
Real-time synchronous (can take up to 3 seconds) - the funds are held by the
customer's bank for around a week, waiting for the settle transaction.

2-stage
Perform an auth transaction for the first one
Use a 'delayed capture' for the first settle and a 'reference transaction' for
any later ones.



PayPal provide SKDs for Java and .NET but no Python (boo)o

This implementation uses the Name-Value pair mode (not XMLPay)

.. note::

    This version of the library was built using the PP_PayflowPro_Guide.pdf
    found in the docs.

---------------
Getting started
---------------

Register a new acccount with PayPal.
Create a PayFlow pro account with PayPal - you will need a:

* Vendor ID
* User (often same as vendor ID)
* Password
* Partner ID (normally "PayPal")

-------------
Not supported
-------------

-------
Testing
-------

See page 49 of the PDF guide for test bankcard numbers

* 5555555555554444
