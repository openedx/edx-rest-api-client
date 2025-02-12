.PHONY: quality requirements test upgrade validate

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

quality:
	tox -e quality

requirements: ## install development environment requirements
	pip install -qr requirements/pip.txt
	pip install -qr requirements/pip-tools.txt
	pip-sync requirements/dev.txt requirements/private.*

test:
	tox

piptools:
	pip install -q -r requirements/pip-tools.txt

define COMMON_CONSTRAINTS_TEMP_COMMENT
# This is a temporary solution to override the real common_constraints.txt\n# In edx-lint, until the pyjwt constraint in edx-lint has been removed.\n# See BOM-2721 for more details.\n# Below is the copied and edited version of common_constraints\n
endef

COMMON_CONSTRAINTS_TXT=requirements/common_constraints.txt
.PHONY: $(COMMON_CONSTRAINTS_TXT)
$(COMMON_CONSTRAINTS_TXT):
	wget -O "$(@)" https://raw.githubusercontent.com/edx/edx-lint/master/edx_lint/files/common_constraints.txt || touch "$(@)"
	echo "$(COMMON_CONSTRAINTS_TEMP_COMMENT)" | cat - $(@) > temp && mv temp $(@)


export CUSTOM_COMPILE_COMMAND = make upgrade
compile-requirements: piptools $(COMMON_CONSTRAINTS_TXT)	## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	# Make sure to compile files after any other files they include!
	pip-compile ${COMPILE_OPTS} --allow-unsafe --rebuild -o requirements/pip.txt requirements/pip.in
	pip-compile ${COMPILE_OPTS} --allow-unsafe --verbose --rebuild -o requirements/pip-tools.txt requirements/pip-tools.in
	pip install -qr requirements/pip.txt
	pip install -qr requirements/pip-tools.txt
	pip-compile ${COMPILE_OPTS}  --allow-unsafe --verbose --rebuild -o requirements/base.txt requirements/base.in
	pip-compile ${COMPILE_OPTS}  --allow-unsafe --verbose --rebuild -o requirements/test.txt requirements/test.in
	pip-compile ${COMPILE_OPTS}  --allow-unsafe --verbose --rebuild -o requirements/dev.txt requirements/dev.in
	pip-compile ${COMPILE_OPTS}  --allow-unsafe --verbose --rebuild -o requirements/pip-tools.txt requirements/pip-tools.in
	pip-compile ${COMPILE_OPTS}  --allow-unsafe --verbose --rebuild -o requirements/ci.txt requirements/ci.in
	# Let tox control the Django and DRF versions for tests
	sed -i.tmp '/^django==/d' requirements/test.txt
	sed -i.tmp '/^djangorestframework==/d' requirements/test.txt
	rm requirements/test.txt.tmp

upgrade:  ## update the pip requirements files to use the latest releases satisfying our constraints
	$(MAKE) compile-requirements COMPILE_OPTS="--upgrade"

validate: test quality
