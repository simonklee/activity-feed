#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, Extension

setup(
    name='activity',
    version='2.5.2',
    description='Activity feeds backed by Redis',
    long_description=codecs.open('readme.md', "r", "utf-8").read(),
    author='Simon Zimmermann',
    author_email='simon@insmo.com',
    url='http://github.com/simonz05/activity-feed',
    license='MIT',
    keywords="redis",
    packages=['activity_feed'],
    ext_modules=[
        Extension('activity_feed.app', sources=['activity_feed/app.c'])
    ],
    install_requires=[
        'redis',
        'leaderboard >= 2.3.0'],
    zip_safe=True,
    test_suite="nose.collector",
    tests_require=['nose'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
    ],
)
