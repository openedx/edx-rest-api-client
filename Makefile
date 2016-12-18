quality:
	tox -e quality

requirements:
	pip install -r test_requirements.txt

test:
	tox

validate: test quality
