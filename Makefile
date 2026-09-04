.PHONY: quality requirements test upgrade validate

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

quality: ## check coding style with pycodestyle and pylint
	uv sync --group quality
	DJANGO_SETTINGS_MODULE=test_settings PYTHONPATH=. uv run pycodestyle --config=.pep8 src/edx_rest_api_client
	DJANGO_SETTINGS_MODULE=test_settings PYTHONPATH=. uv run pylint --rcfile=pylintrc src/edx_rest_api_client
	uv run python -m build
	uv run twine check dist/*

requirements: ## install development environment requirements
	uv sync --group dev

test: ## run tests in the current virtualenv
	uv run tox

upgrade: ## update the uv.lock file with the latest packages satisfying pyproject.toml
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

validate: test quality
