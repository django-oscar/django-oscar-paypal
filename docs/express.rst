================
Express checkout
================

`PayPal Express` is an API for integrating PayPal payments into an ecommerce
site.  A typical implementation involves redirecting the user to PayPal's site
where they enter their shipping and billing information before arriving back on
the merchant site to confirm the order.  It can also be used purely for payment,
with shipping details being collected on the merchant site.

Oscar also supports a dashboard for PayPal Express transactions, which
integrates with Oscar's dashboard.

See the `PDF documentation`_ for the gory details of PayPal Express.

.. _`PayPal Express`: https://www.paypal.com/uk/cgi-bin/webscr?cmd=_additional-payment-ref-impl1
.. _`PDF documentation`: https://www.paypalobjects.com/webstatic/en_US/developer/docs/pdf/pp_expresscheckout_integrationguide.pdf

---------------
Getting started
---------------

You need to create a PayPal sandbox account which is different from your normal
paypal account then use this account to create two 'test' users: a buyer and a
seller.  Once the seller is created, you will have access to a
username, password and 'signature' which are used to authenticate API
requests.

Add the following settings using the details from your sandbox seller account::

    PAYPAL_API_USERNAME = 'test_xxxx.gmail.com'
    PAYPAL_API_PASSWORD = '123456789'
    PAYPAL_API_SIGNATURE = '...'

Next, you need to add the PayPal URLs to your URL config.  This can be done as
follows::

    from django.contrib import admin
    from django.urls import include, path

    from oscar.app import shop
    
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('checkout/paypal/', include('paypal.express.urls')),
        # Optional
        path('dashboard/paypal/express/', apps.get_app_config("express_dashboard").urls),
        path('', shop.urls),
    ]

If you are using the dashboard views, extend the dashboard navigation to include
the appropriate links and add the dashboard app to INSTALLED_APPS in settings.py:: 
    
    INSTALLED_APPS += ['paypal.express.dashboard.apps.ExpressDashboardApplication']
    
    # Add Payflow dashboard stuff to settings
    from django.utils.translation import gettext_lazy as _
    OSCAR_DASHBOARD_NAVIGATION.append(
        {
            'label': _('PayPal'),
            'icon': 'icon-globe',
            'children': [
                {
                    'label': _('Express transactions'),
                    'url_name': 'express_dashboard:paypal-express-list',
                },
            ]
        })

Finally, you need to modify oscar's basket template to include the button that
links to PayPal.  This can be done by creating a new template
``templates/basket/partials/basket_content.html`` with content::

    {% extends 'oscar/basket/partials/basket_content.html' %}
    {% load i18n %}

    {% block formactions %}
    <div class="form-actions">
        {% if anon_checkout_allowed or request.user.is_authenticated %}
            <a href="{% url 'paypal-redirect' %}"><img src="https://www.paypal.com/en_US/i/btn/btn_xpressCheckout.gif" align="left" style="margin-right:7px;"></a>
        {% endif %}
        <a href="{% url 'checkout:index' %}" class="pull-right btn btn-large btn-primary">{% trans "Proceed to checkout" %}</a>
    </div>
    {% endblock %}

Note that we are extending the ``basket/partials/basket_content.html`` template
from oscar and overriding the ``formactions`` block.  For this trick to work,
you need to ensure that you have ``OSCAR_MAIN_TEMPLATE_DIR`` in your
``TEMPLATE_DIRS`` after your local templates setting::

    from oscar import OSCAR_MAIN_TEMPLATE_DIR
    TEMPLATE_DIRS = (
        location('templates'),
        OSCAR_MAIN_TEMPLATE_DIR,
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
* ``PAYPAL_CALLBACK_HTTPS`` - whether to use HTTPS for the callback URLs passed
  to PayPal. Defaults to ``True``.
* ``PAYPAL_CURRENCY`` - the currency to use for transactions.  Defaults to ``GBP``.
* ``PAYPAL_API_VERSION`` - the version of API used (defaults to ``119``)
* ``PAYPAL_ALLOW_NOTE`` - whether to allow the customer to enter a note (defaults to ``True``)
* ``PAYPAL_CUSTOMER_SERVICES_NUMBER`` - customer services number to display on
  the PayPal review page.
* ``PAYPAL_HEADER_IMG`` - the absolute path to a header image
* ``PAYPAL_HEADER_BACK_COLOR`` - background color (6-char hex value) for header
  background
* ``PAYPAL_HEADER_BORDER_COLOR`` - background color (6-char hex value) for header border
* ``PAYPAL_CALLBACK_TIMEOUT`` - timeout in seconds for the instant update
  callback
* ``PAYPAL_SOLUTION_TYPE`` - type of checkout flow ('Sole' or 'Mark')
* ``PAYPAL_LANDING_PAGE`` - type of PayPal page to display ('Billing' or 'Login')
* ``PAYPAL_BRAND_NAME`` - a label that overrides the business name in the PayPal
  account on the PayPal hosted checkout pages
* ``PAYPAL_PAGESTYLE`` - name of the Custom Payment Page Style for payment pages
  associated with this button or link
* ``PAYPAL_PAYFLOW_COLOR`` - background color (6-char hex value) for the payment page
* ``PAYPAL_BUYER_PAYS_ON_PAYPAL`` - If ``True`` you can shorten your checkout flow to
  let buyers complete their purchases on PayPal. The order confirmation page is skipped (defaults to ``False``)


Some of these options, like the display ones, can be set in your PayPal merchant
profile.

You can also override the raw paypal params by defining a new
paypal.express.views.RedirectView and define the ``_get_paypal_params``
method::

    from paypal.express.views import RedirectView as OscarPaypalRedirectView


    class RedirectView(OscarPaypalRedirectView):
        def _get_paypal_params(self):
            return {
                'SOLUTIONTYPE': 'Mark',
                'LANDINGPAGE': 'Login',
                'BRANDNAME': 'My Brand name'
            }

Please note that all the dynamic paypal params (e.g. amount, return_url,
cancel_url etc.) cannot be overridden by ``_get_paypal_params``.


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
