import unittest

import datetime

from activity import Activity
from activity.utils import datetime_to_timestamp, utcnow

def timestamp(*args):
    return datetime_to_timestamp(datetime.datetime(*args))

def timestamp_utcnow():
    return datetime_to_timestamp(utcnow())

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.a = Activity(redis='redis://:@localhost:6379/15')
        self._empty()

    def _empty(self):
        a = self.a
        keys = a.redis.keys('{}*'.format(a.namespace))

        if keys:
            a.redis.delete(*keys)

    def add_items_to_feed(self, user_id, items_to_add=5, aggregate=None):
        """Helper method to add items to a given feed.

        :param items_to_add: [int] Number of items to add to the feed.
        """
        if aggregate is None:
            aggregate = self.a.aggregate

        now = timestamp_utcnow()

        for i in range(1, items_to_add + 1):
            self.a.update_item(user_id, i, now, aggregate)
            now += 5
