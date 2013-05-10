# -*- coding: utf-8 -*-

import unittest

from activity import Activity
from activity.utils import datetime_to_timestamp, utcnow

class FeedTest(unittest.TestCase):
    def setUp(self):
        self._empty()

    def _empty(self):
        a = Activity()
        keys = a.redis.keys('{}*'.format(a.config['NAMESPACE']))

        if keys:
            a.redis.delete(*keys)
