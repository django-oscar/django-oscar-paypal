#!/bin/bash

DATABASE=db.sqlite
USER=admin
EMAIL=admin@test.com

rm $DATABASE
./manage.py syncdb --noinput
./manage.py migrate
./manage.py oscar_import_catalogue data/books-catalogue.csv
./manage.py loaddata countries.json

echo "Creating superuser '$USER' with email '$EMAIL'"
./manage.py createsuperuser --username=$USER --email=$EMAIL