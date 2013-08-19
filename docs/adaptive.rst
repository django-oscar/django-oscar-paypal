=================
Adaptive payments
=================

`Adaptive Payments`_ is a product that supports a variety of complex payment
scenarios.  This extension supports making parallel or chained payments using
the "Pay" API.

Getting started
---------------

Credentials
~~~~~~~~~~~

You will need the user ID, password and signature from your PayPal account, and
also an application ID.  These are used to authenticate requests.

Creating payments
~~~~~~~~~~~~~~~~~

To create a payment going to multiple receivers, you need to build a list of
receiver data.  Use the ``Receiver`` class from the ``paypal.adaptive.gateway`` module.

.. code:: python

   from paypal.adaptive import gateway

    receivers = (
        gateway.Receiver(email='receiver1@gmail.com',
                         amount=D('12.00'), is_primary=False),
        gateway.Receiver(email='receiver2@gmail.com',
                         amount=D('10.00'), is_primary=False),
    )

and submit this data along with the success and cancel URLs for your
application:

.. code:: python

    txn = gateway.pay(
        receivers=receivers,
        currency='GBP',
        return_url='http://example.com/paypal/success/',
        cancel_url='http://example.com/paypal/cancel/',
        ip_address=self.request.META['REMOTE_ADDR'])

.. note::

   This package doesn't provide success and cancel views as these are specific
   to your application.

This will attempt to create the payment using PayPal's API.  If this is
successul, you can redirect the user to PayPal to confirm the transaction:

.. code:: python

    if txn.is_successful:
        return http.HttpResponseRedirect(txn.redirect_url)

It makes sense to persist the "pay key" in the user's session so you can query
the results of the transaction when the user lands on the success URL:

.. code:: python

   txn = gateway.details(pay_key)
   if txn.is_complete:
       # Payment is complete

And that's about it - enjoy!


Not supported (yet)
-------------------

- Pre-approved payments
- IPN notification handling
- Create and execute payments
