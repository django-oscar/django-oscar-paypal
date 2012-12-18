================
Express checkout
================

`PayPal Express` is an API for integrating PayPal payments into an ecommerce
site.  A typical implementation involves redirecting the user to PayPal's site
where they enter their shipping and billing information before arriving back on
the merchant site to confirm the order.  It can also be used purely for payment,
with shipping details being collected on the merchant site.

See the `PDF documentation`_ for the gory details of PayPal Express.

.. _`PayPal Express`: https://www.paypal.com/uk/cgi-bin/webscr?cmd=_additional-payment-ref-impl1
.. _`PDF documentation`: https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_ExpressCheckout_IntegrationGuide.pdf

---------------
Getting started
---------------

You need to create a PayPal sandbox account which is different from your normal
paypal account then use this account to create two 'test' users: a buyer and a
seller.  Once the seller is created, you will have access to a
username, password and 'signature' which are used to authenticate API
requests.

Add the following settings using the details from your sandbox buyer account::

    PAYPAL_API_USERNAME = 'test_xxxx.gmail.com'
    PAYPAL_API_PASSWORD = '123456789'
    PAYPAL_API_SIGNATURE = '...'

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
installation is set-up.  This is a working Oscar install that uses PayPal
Express.

--------
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

Some of these options, like the display ones, can be set in your PayPal merchant
profile.

----------------
PayPal Dashboard
----------------

You can view the merchant dashboard in PayPal's sandbox site by logging in as
the sandbox master user, selecting the test seller account in the 'Test
Accounts' tab then clicking 'Enter sandbox'.

------------
Not included
------------

The following options are part of the PayPal Express API but are not handled
within this implementation - mainly as it's not obvious how you can handle
these in a 'generic' way within Oscar:

* Gift wrapping
* Buyer consent to receive promotional emails
* Survey questions
* User confirming order on PayPal (bypassing review stage)
* Recurring payments
* Fraud management

------------
Known issues
------------

* Vouchers may have expired during the time when the user is on the PayPal site.
