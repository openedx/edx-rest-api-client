ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
PACKAGE = ecommerce_api_client

validate: requirements test quality

requirements:
	pip install -q -r requirements.txt

test:
	nosetests --with-coverage --cover-inclusive --cover-branches \
		--cover-html --cover-html-dir=$(COVERAGE)/html/ \
		--cover-xml --cover-xml-file=$(COVERAGE)/coverage.xml \
		--cover-package=$(PACKAGE) $(PACKAGE)/

quality:
	pep8 --config=.pep8 $(PACKAGE)
	pylint --rcfile=.pylintrc $(PACKAGE)
