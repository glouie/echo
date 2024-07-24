.PHONY: clean-pyc clean-build docs clean

PACKAGE=echo

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "install_dev - install dependencies to run lint, test, publishing, etc"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

install_dev:
	pip install -r ./requirements_dev.txt

lint: install_dev
	flake8 html tests

test: lint install_dev develop
	py.test tests -k "not tests/webdriver"

coverage:
	coverage run --source html setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

develop: clean uninstall
	pip install -e .

install: clean uninstall
	pip install .

uninstall:
	pip uninstall -y $(PACKAGE) || true

dist: clean
	python setup.py sdist
	ls -l dist

bdist: clean
	pip install wheel
	python setup.py bdist_wheel
	ls -l dist

githooks:
	cp ./pre-push ./.git/hooks
