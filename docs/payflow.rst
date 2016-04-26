===========
Payflow Pro
===========

Payflow Pro is a server-to-server payment option for businesses who have a
merchant account.  Unlike Express Checkout, it doesn't require redirecting the
user to PayPal's site and allows a customer to use a normal bankcard instead of
their PayPal account.  `Read more details on the PayPal site`_.

.. _`Read more details on the PayPal site`: https://www.paypal.com/webapps/mpp/payflow-payment-gateway

.. note::

    This version of the library was built using the PP_PayflowPro_Guide.pdf
    guide found in the docs/guides folder.  It is recommended that developers at
    least skim-read this guide so that they are familiar with the overall
    processes.  It also has magic bankcard numbers that can be used for testing.
    `Find the latest developer docs on the PayPal site`_.

.. _`Find the latest developer docs on the PayPal site`: https://developer.paypal.com/docs/classic/products/payflow/

---------------
Getting started
---------------

You'll need to create an Payflow account with PayPal in order to get a:

* Vendor ID
* Username (usually same as vendor ID)
* Password
* Partner ID (normally "PayPal" when you register directly with PayPal)

In practice, you only really need a vendor ID and a password.  Add settings to
your project with your credentials::

    # settings.py
    ...
    PAYPAL_PAYFLOW_VENDOR_ID = 'mypaypalaccount'
    PAYPAL_PAYFLOW_PASSWORD = 'asdfasdfasdf'

----------
Next steps
----------

The next steps are to plumb the payment gateway into your checkout and order
processing.  There is no one-size-fits-all solution here - your implementation
will depend on your business model.  

A good way to start is to browse the sandbox project within the repo - this is a
fully integrated Oscar site.

Note that in an Oscar site, you should only consume the API of the
``paypal.payflow.facade`` module.

For checkout integration, you'll typically want the ``PaymentDetailsView`` in
the following ways:

* Override the ``get_context_data`` method to provide a bankcard and billing
  address form.

* Override the ``post`` method to validate the forms and render them again in
  the preview view (but hidden).

* Override the ``handle_payment`` method of your checkout's
  ``PaymentDetailsView`` to call either the ``authorize`` or ``sale`` method of
  the facade depending on whether you are using one- or two-stage payment
  processing.

For general order processing integration, you'll likely need to adjust your
``EventHandler`` to make calls to the PayPal facade when certain shipping events
occur.  For instance, you may call ``delayed_capture`` when items ship in order
to capture the funds at that stage.

You can log into your Payflow account to manage transactions under review and
view reports.
https://manager.paypal.com/

--------
Settings
--------

Required settings:

``PAYPAL_PAYFLOW_VENDOR_ID``
    Your merchant login ID created when you registered the account with PayPal.
``PAYPAL_PAYFLOW_PASSWORD``
    Your merchant password.

Optional settings:

``PAYPAL_PAYFLOW_CURRENCY``
    The 3 character currency code to use for transactions.  Defaults to 'USD'.
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

-------------------
Using without Oscar
-------------------

To use Payflow Pro without an Oscar install, you need to use the
``paypal.payflow.gateway`` module directly.  This module is agnostic of Oscar
and can be used independently.  

The ``paypal.payflow.facade`` module is a bridging module that provides a
simpler API designed to link Oscar to the gateway module.

---
API
---

Facade
------

.. automodule:: paypal.payflow.facade
    :members:

Gateway
-------

.. automodule:: paypal.payflow.gateway
    :members:


