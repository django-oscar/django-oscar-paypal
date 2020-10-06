#!/usr/bin/env python
from setuptools import find_packages, setup

from paypal import VERSION

setup(
    name='django-oscar-paypal',
    version=VERSION,
    url='https://github.com/django-oscar/django-oscar-paypal',
    description=(
        "Integration with PayPal Express, PayPal Payflow Pro and Adaptive "
        "Payments for django-oscar"),
    long_description=open('README.rst').read(),
    keywords="Payment, PayPal, Oscar",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'django>=2.2,<2.3',
        'paypal-checkout-serversdk>=1.0.1',
        'requests>=1.0',
        'django-localflavor'
    ],
    extras_require={
        'oscar': ['django-oscar>=2.0,<2.2']
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Other/Nonlisted Topic'],
)
