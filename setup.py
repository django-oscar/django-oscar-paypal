#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-oscar-paypal',
      version='0.1.1',
      url='https://github.com/tangentlabs/django-oscar-paypal',
      author="David Winterbottom",
      author_email="david.winterbottom@tangentlabs.co.uk",
      description="PayPal payment module for django-oscar",
      long_description=open('README.rst').read(),
      keywords="Payment, PayPal",
      license='BSD',
      platforms=['linux'],
      packages=find_packages(),
      include_package_data = True,
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: Unix',
                   'Programming Language :: Python'],
      install_requires=['django-oscar==0.2.1',
                        'requests==0.13.1',
                        'purl==0.4'],
      )
