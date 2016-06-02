all: clean-pyc test

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-so:
	find . -name '*.so' -exec rm -f {} +

test:
	@nosetests -s -w tests

test_setup:
	@python scripts/test_setup.py

toxtest:
	@tox

activity_feed/_utils_speedups.so: activity_feed/_utils_speedups.pyx
	cython activity_feed/_utils_speedups.pyx
	python setup.py build
	cp build/*/activity_feed/_utils_speedups*.so activity_feed
	
pypi-upload:
	python setup.py sdist --formats=gztar upload

cybuild: clean-so activity_feed/_utils_speedups.so

.PHONY: test clean-pyc clean-so cybuild pypi-upload all
