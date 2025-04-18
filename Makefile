.DEFAULT_GOAL := help

SHELL=/bin/bash
VENV = .venv.make

# Detect the operating system and set the virtualenv bin directory
ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

setup: $(VENV)/bin/activate

startup:
	@sh ./.script/setup.sh

$(VENV)/bin/activate: $(VENV)/.venv-timestamp

$(VENV)/.venv-timestamp: uv.lock
	# Create new virtual environment if setup.py has changed
	uv venv --python 3.13 $(VENV)
	uv pip install --prefix $(VENV) ruff
	uv pip install --prefix $(VENV) mypy
	uv pip install --prefix $(VENV) pytest
	touch $(VENV)/.venv-timestamp

testenv: $(VENV)/.testenv

$(VENV)/.testenv: $(VENV)/bin/activate
	# check uv version and use appropriate parameters
#	if . $(VENV_BIN)/activate && uv sync --help | grep -q -- "--active"; then \
#		. $(VENV_BIN)/activate && uv sync --active --all-packages \
#			--extra "base" \
#			--extra "proxy_openai" \
#			--extra "rag" \
#			--extra "storage_chromadb" \
#			--extra "dbgpts" \
#			--link-mode=copy; \
#	else \
#		. $(VENV_BIN)/activate && uv sync --all-packages \
#			--extra "base" \
#			--extra "proxy_openai" \
#			--extra "rag" \
#			--extra "storage_chromadb" \
#			--extra "dbgpts" \
#			--link-mode=copy; \
#	fi
#	cp .devcontainer/dbgpt.pth $(VENV)/lib/python3.11/site-packages
#	touch $(VENV)/.testenv


.PHONY: fmt
fmt: setup ## Format Python code
	# Format code
	$(VENV_BIN)/ruff format packages
	# Sort imports
	$(VENV_BIN)/ruff check --select I --fix packages

.PHONY: fmt-check
fmt-check: setup ## Check Python code formatting and style without making changes
	$(VENV_BIN)/ruff format --check packages
	$(VENV_BIN)/ruff check --select I packages

.PHONY: pre-commit
pre-commit: fmt-check test test-doc mypy ## Run formatting and unit tests before committing

test: $(VENV)/.testenv ## Run unit tests
	#$(VENV_BIN)/pytest --pyargs dbgpt

.PHONY: test-doc
test-doc: $(VENV)/.testenv ## Run doctests
	# -k "not test_" skips tests that are not doctests.
	#$(VENV_BIN)/pytest --doctest-modules -k "not test_" dbgpt/core

.PHONY: mypy
mypy: $(VENV)/.testenv ## Run mypy checks
	# https://github.com/python/mypy
	# $(VENV_BIN)/mypy --exclude '/(site-packages|node_modules|__pycache__|\..*)/$' --ignore-missing-imports packages/*

.PHONY: coverage
coverage: setup ## Run tests and report coverage
	#$(VENV_BIN)/pytest --pyargs dbgpt --cov=dbgpt

.PHONY: clean
clean: ## Clean up the environment
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	# find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.coverage' -delete

.PHONY: clean-dist
clean-dist: ## Clean up the distribution
	rm -rf dist/ *.egg-info build/

.PHONY: build
build: clean-dist ## Package the project for distribution
	uv build --all-packages
#	rm -rf dist/dbgpt_app-*
#	rm -rf dist/dbgpt_serve-*

.PHONY: publish
publish: build ## Upload the package to PyPI
	uv publish

.PHONY: publish-test
publish-test: build ## Upload the package to PyPI
	uv publish --index testpypi

.PHONY: help
help:  ## Display this help screen
	@echo "Available commands:"
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort