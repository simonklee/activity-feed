# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .helper import BaseTest, timestamp_utcnow

class ItemTest(BaseTest):
    def update_item_test(self):
        'should correctly build an activity feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)

        self.a.update_item('david', 1, timestamp_utcnow())

        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)

    def update_item_aggregation_test(self):
        'should correctly build an activity feed with an aggregate activity_feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), False)

        self.a.update_item('david', 1, timestamp_utcnow(), True)

        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), True)

    def add_item_test(self):
        'should correctly build an activity feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)

        self.a.add_item('david', 1, timestamp_utcnow())
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)

    def add_item_aggregation_test(self):
        'should correctly add an item into an aggregate activity feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), False)

        self.a.add_item('david', 1, timestamp_utcnow(), True)

        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), True)

    def remove_item_test(self):
        'should remove an item from an activity feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 0)

        self.a.update_item('david', 1, timestamp_utcnow())

        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 1)

        self.a.remove_item('david', 1)

        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 0)

    def remove_item_aggregation_test(self):
        'should remove an item from an activity feed and the aggregate feed'
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), False)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), False)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 0)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david', True)), 0)

        self.a.update_item('david', 1, timestamp_utcnow(), True)

        self.assertEqual(self.a.redis.exists(self.a.feed_key('david')), True)
        self.assertEqual(self.a.redis.exists(self.a.feed_key('david', True)), True)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 1)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david', True)), 1)

        self.a.remove_item('david', 1)

        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david')), 0)
        self.assertEqual(self.a.redis.zcard(self.a.feed_key('david', True)), 0)

    def check_item_test(self):
        'should return whether or not an item exists in the feed'
        self.assertEqual(self.a.check_item('david', 1), False)
        self.a.add_item('david', 1, timestamp_utcnow())
        self.assertEqual(self.a.check_item('david', 1), True)

    def check_item_aggregation_test(self):
        'should return whether or not an item exists in the feed'
        self.a.aggregate = True
        self.assertEqual(self.a.check_item('david', 1, True), False)
        self.a.add_item('david', 1, timestamp_utcnow())
        self.assertEqual(self.a.check_item('david', 1, True), True)
