# -*- coding: utf-8 -*-

import unittest

from activity import Activity
from activity.utils import datetime_to_timestamp, utcnow

class ItemTest(unittest.TestCase):

    def setUp(self):
        self._empty()

    def _empty(self):
        a = Activity()
        keys = a.redis.keys('{}*'.format(a.namespace))

        if keys:
            a.redis.delete(*keys)

    def update_item_test(self):
        'should correctly build an activity feed'
        a = Activity()

        self.assertEqual(a.redis.exists(a.feed_key('david')), False)

        a.update_item('david', 1, datetime_to_timestamp(utcnow()))

        self.assertEqual(a.redis.exists(a.feed_key('david')), True)

    def update_item_aggregation_test(self):
        'should correctly build an activity feed with an aggregate activity_feed'
        a = Activity()

        self.assertEqual(a.redis.exists(a.feed_key('david')), False)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), False)

        a.update_item('david', 1, datetime_to_timestamp(utcnow()), True)

        self.assertEqual(a.redis.exists(a.feed_key('david')), True)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), True)

    def add_item_test(self):
        'should correctly build an activity feed'
        a = Activity()
        self.assertEqual(a.redis.exists(a.feed_key('david')), False)

        a.add_item('david', 1, datetime_to_timestamp(utcnow()))
        self.assertEqual(a.redis.exists(a.feed_key('david')), True)

    def add_item_aggregation_test(self):
        'should correctly add an item into an aggregate activity feed'
        a = Activity()

        self.assertEqual(a.redis.exists(a.feed_key('david')), False)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), False)

        a.add_item('david', 1, datetime_to_timestamp(utcnow()), True)

        self.assertEqual(a.redis.exists(a.feed_key('david')), True)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), True)

    def remove_item_test(self):
        'should remove an item from an activity feed'
        a = Activity()

        self.assertEqual(a.redis.exists(a.feed_key('david')), False)
        self.assertEqual(a.redis.zcard(a.feed_key('david')), 0)

        a.update_item('david', 1, datetime_to_timestamp(utcnow()))

        self.assertEqual(a.redis.exists(a.feed_key('david')), True)
        self.assertEqual(a.redis.zcard(a.feed_key('david')), 1)

        a.remove_item('david', 1)

        self.assertEqual(a.redis.zcard(a.feed_key('david')), 0)

    def remove_item_aggregation_test(self):
        'should remove an item from an activity feed and the aggregate feed'
        a = Activity()
        self.assertEqual(a.redis.exists(a.feed_key('david')), False)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), False)
        self.assertEqual(a.redis.zcard(a.feed_key('david')), 0)
        self.assertEqual(a.redis.zcard(a.feed_key('david', True)), 0)

        a.update_item('david', 1, datetime_to_timestamp(utcnow()), True)

        self.assertEqual(a.redis.exists(a.feed_key('david')), True)
        self.assertEqual(a.redis.exists(a.feed_key('david', True)), True)
        self.assertEqual(a.redis.zcard(a.feed_key('david')), 1)
        self.assertEqual(a.redis.zcard(a.feed_key('david', True)), 1)

        a.remove_item('david', 1)

        self.assertEqual(a.redis.zcard(a.feed_key('david')), 0)
        self.assertEqual(a.redis.zcard(a.feed_key('david', True)), 0)

    def check_item_test(self):
        'should return whether or not an item exists in the feed'
        a = Activity(aggregate=False)

        self.assertEqual(a.check_item('david', 1), False)
        a.add_item('david', 1, datetime_to_timestamp(utcnow()))
        self.assertEqual(a.check_item('david', 1), True)

    def check_item_aggregation_test(self):
        'should return whether or not an item exists in the feed'
        a = Activity(aggregate=True)

        self.assertEqual(a.check_item('david', 1, True), False)
        a.add_item('david', 1, datetime_to_timestamp(utcnow()))
        self.assertEqual(a.check_item('david', 1, True), True)
