#!/usr/bin/env python
from setuptools import setup, find_packages

from paypal import VERSION

setup(name='django-oscar-paypal',
      version=VERSION,
      url='https://github.com/tangentlabs/django-oscar-paypal',
      author="David Winterbottom",
      author_email="david.winterbottom@tangentlabs.co.uk",
      description="PayPal payment module for django-oscar",
      long_description=open('README.rst').read(),
      keywords="Payment, PayPal, Oscar",
      license=open('LICENSE').read(),
      platforms=['linux'],
      packages=find_packages(exclude=['sandbox*', 'tests*']),
      include_package_data=True,
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Topic :: Other/Nonlisted Topic'],
      install_requires=[
          'django-oscar>=0.5',
          'requests>=1.0',
          'purl>=0.4'],
      )
