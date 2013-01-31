============
Contributing
============

Do this::

    mkvirtualenv oscar-paypal
    git clone git://github.com/tangentlabs/django-oscar-paypal.git
    cd django-oscar-paypal
    python setup.py develop
    pip install -r requirements.txt

then you should be able to run the tests using::

    ./runtests.py

There is also a sandbox site for exploring a sample oscar site.  Set it up::

    cd sandbox
    ./manage.py syncdb --noinput
    ./manage.py migrate
    ./manage.py oscar_import_catalogue data/books-catalogue.csv

and run it::

    ./manage.py runserver

Use the `Github issue tracker`_ for any problems.

.. _`Github issue tracker`: https://github.com/tangentlabs/django-oscar-paypal/issues
