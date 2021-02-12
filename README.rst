===============================
PayPal package for django-oscar
===============================

This package provides integration between django-oscar_ and both `PayPal REST API`_, `PayPal
Express (NVP)`_ and `PayPal Payflow Pro`_.

.. _django-oscar: https://github.com/django-oscar/django-oscar
.. _`PayPal REST API`: https://developer.paypal.com/docs/api-basics/
.. _`PayPal Express (NVP)`: https://developer.paypal.com/docs/nvp-soap-api/
.. _`PayPal Payflow Pro`: https://merchant.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=merchant/payment_gateway

These payment options can be used individually or together.  Further, the
package is structured so that it can be used without Oscar if you so wish.

* `Full documentation`_

.. _`Full documentation`: https://django-oscar-paypal.readthedocs.io/en/latest/
.. _`Continuous integration status`: http://travis-ci.org/#!/django-oscar/django-oscar-paypal?branch=master

License
-------

The package is released under the `New BSD license`_.

.. _`New BSD license`: https://github.com/django-oscar/django-oscar-paypal/blob/master/LICENSE

Support
-------

Having problems or got a question?

* Have a look at the sandbox site as this is a sample Oscar project
  integrated with both PayPal options.  See the `contributing guide`_ within the
  docs for instructions on how to set up the sandbox locally.

* Ping `@django_oscar`_ with quick queries.

* Ask more detailed questions on the Oscar mailing list: `django-oscar@googlegroups.com`_

* Use Github_ for submitting issues and pull requests.

.. _`@django_oscar`: https://twitter.com/django_oscar
.. _`contributing guide`: https://django-oscar-paypal.readthedocs.io/en/latest/contributing.html
.. _`django-oscar@googlegroups.com`: https://groups.google.com/forum/?fromgroups#!forum/django-oscar
.. _`Github`: http://github.com/django-oscar/django-oscar-paypal

Tests
-----

.. image:: https://github.com/django-oscar/django-oscar-paypal/workflows/Tests/badge.svg

.. image:: http://codecov.io/github/django-oscar/django-oscar-paypal/coverage.svg?branch=master
    :alt: Coverage
    :target: http://codecov.io/github/django-oscar/django-oscar-paypal?branch=master

Changelog
---------

2.0.0 (released December 20th, 2019)
------------------------------------
* Add support for Oscar 2.0 and Django 2.2.
* Drop support for Oscar 1.6 and lower and Django 2.0 and lower.
* Drop support for Python 2.

1.0.0 (released May 30th, 2018)
-----------------------------------
* Add support for Oscar 1.6 and Django 2.
* Drop support for Oscar 1.4 and lower and Django 1.10 and lower.

0.9.7 (released January 12th, 2016)
-----------------------------------
* Fix breakage when using Oscar's ``DeferredTaxMixin``. `#98`_ `#121`_

.. _`#98`: https://github.com/django-oscar/django-oscar-paypal/issues/98
.. _`#121`: https://github.com/django-oscar/django-oscar-paypal/pull/121

0.9.6 (released November 13th, 2015)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Add support for Oscar 1.1 and Django 1.8.
* Drop support for Django 1.6 and Oscar 0.7.
* Store submitted shipping method instead of falling back to ``FixedPrice``. `#107`_
* Display original Paypal error message instead of generic error message. `#101`_
* Bugfix: Hide form buttons as expected. `#94`_
* Bugfix: Correct signature for call to ``get_shipping_methods``. `#99`_
* Bugfix: Don't fail in countries without postcode. `#100`_

.. _`#94`: https://github.com/django-oscar/django-oscar-paypal/pull/94
.. _`#99`: https://github.com/django-oscar/django-oscar-paypal/issues/99
.. _`#100`: https://github.com/django-oscar/django-oscar-paypal/issues/100
.. _`#101`: https://github.com/django-oscar/django-oscar-paypal/pull/101
.. _`#107`: https://github.com/django-oscar/django-oscar-paypal/pull/107

0.9.5
~~~~~
* Fix issue with missing templates in PyPI package.

0.9.4
~~~~~

* Use Bankcard.number instead of the deprecated Bankcard.card_number attribute.
* Add support for Django 1.7 and Oscar 1.0.
* Drop support for Oscar 0.6 and Django 1.5.

0.9.3
~~~~~

* Use the correct key to look up a previous transaction ID (for
  refund/capture/void operations). `#81`_

.. _`#81`: https://github.com/django-oscar/django-oscar-paypal/pull/81

0.9.2
~~~~~

* Include templates in package (they were missing from 0.9.1)
* Dynamically load view classes in Express views module

0.9.1
~~~~~

* Add support for Python 3.3 and 3.4
* Add preliminary support for (unreleased) Oscar 0.8

0.9
~~~
* Support Oscar 0.7 (note that this release only works with 0.7.1 onwards)
* Drop support for Oscar 0.5
* Fix bug around unicode handling
* Allow scheme of callback URL to be specified in a setting

0.8.1
~~~~~
* Ensure sandbox demo site works correctly with Oscar 0.6
* Fix a bug with Payflow Pro using wrong bankcard attribute for expiry dates.
* Remove Oscar version verification in ``setup.py``
* Use content-type ``text/namevalue`` when submitting key-value pairs to
  PayPal.

0.8
~~~
* Support Oscar 0.6
* Fix bug with offers not being applied to basket on return from PayPal site.

0.7
~~~
* Remove Oscar from ``install_requires``

0.6.1
~~~~~
* Persist shipping method name when using PayPal Express as a payment method
  only.

0.6
~~~
* Add support for ``NO_SHIPPING`` option with PayPal Express.

0.5
~~~
* Addresses a `security issue`_ where baskets could be manipulated while the
  customer was on the PayPal site.  This would cause the final order to contain
  more items that were paid for.

.. _`security issue`: https://github.com/django-oscar/django-oscar-paypal/pull/24

0.4.1
~~~~~
* Fixes a bug where the second line of a user's address was not being used to
  create the order shipping address.

0.4
~~~
* We now require Oscar >= 0.5
* Full i18 support
* New dashboard views for PayPal Express

0.3.3
~~~~~
* Restrict to Oscar < 0.5

0.3.2
~~~~~
* Pass shipping address name when using Express checkout
* Docs update

0.3.1
~~~~~
* Fix issue with currency formatting
* Fix issue with i18n proxies being passed to PayPal

0.3
~~~
* Order discounts are now passed correctly to PayPal as separate lines
* Fix unicode issue when reading data back from PayPal
* Use Tox for testsuite

0.2.5
~~~~~
* Fix silly bug with reference transactions

0.2.4
~~~~~
* Fix bug with installing templates

0.2.3
~~~~~
* Fix bug with amount formats not being validated properly
* Adjust txn model to allow virtually everything to be nullable

0.2.2
~~~~~
* Add support for specifying transaction currency

0.2.1
~~~~~
* Fix packaging issues
* Remove dead templates
* With API docs

0.2
~~~
Includes support for Payflow Pro.

0.1
~~~
Includes support for Express Checkout.
