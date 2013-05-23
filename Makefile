all: clean-pyc test

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

test:
	@nosetests -s -w tests

test_setup:
	@python scripts/test_setup.py

toxtest:
	@tox

activity_feed/_app_speedups.so: activity_feed/_app_speedups.pyx
	cython activity_feed/_app_speedups.pyx
	python setup.py build
	cp build/*/activity_feed/_app_speedups*.so activity_feed

cybuild: activity_feed/_app_speedups.so

.PHONY: test clean-pyc cybuild all
