# -*- coding: utf-8 -*-
"""
ActivityFeed
------------

Activity feeds backed by Redis.
"""

__version__ = "2.6.0"

try:
    from _app_speedups import ActivityFeed
except:
    from _app_python import ActivityFeed

__all__ = ['ActivityFeed']
