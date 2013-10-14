#!/usr/bin/env python
from setuptools import setup, find_packages

from paypal import VERSION


MIN_OSCAR_VERSION = (0, 4)
try:
    import oscar
except ImportError:
    # Oscar not installed
    pass
else:
    # Oscar is installed, assert version is up-to-date
    if oscar.VERSION < MIN_OSCAR_VERSION:
        raise ValueError(
            "Oscar>%s required, current version: %s" % (
                ".".join(MIN_OSCAR_VERSION), oscar.get_version()))


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
          'requests>=1.0',
          'purl>=0.4'],
      )
