.PHONY: help clean clean-pyc clean-build list test sdist venv devbuild devinstall

help:
	@echo "clean       - remove build artifacts and Python file artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc   - remove Python file artifacts"
	@echo "test        - run tests quickly with the default Python"
	@echo "sdist       - package"
	@echo "devinstall  - install Python package in editable mode"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

sdist: clean
	venv/bin/python setup.py sdist
	venv/bin/python setup.py bdist_wheel 
	ls -l dist

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

devbuild: venv
	venv/bin/python setup.py install

devinstall:
	venv/bin/pip install --editable .

test: devbuild
	venv/bin/pytest tests/test_vm.py -v


