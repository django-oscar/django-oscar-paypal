install:
	pip install -r requirements.txt
	python setup.py develop

upgrade:
	pip install -U -r requirements.txt
	python setup.py develop --upgrade

sandbox: install
	-rm -f sandbox/db.sqlite
	sandbox/manage.py migrate --noinput
	sandbox/manage.py loaddata sandbox/fixtures/auth.json countries.json
	sandbox/manage.py oscar_import_catalogue sandbox/fixtures/catalogue.csv

lint:
	flake8 paypal tests setup.py
	isort -q -c --recursive --diff paypal tests setup.py
