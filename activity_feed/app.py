# -*- coding: utf-8 -*-
from __future__ import absolute_import

import redis
import leaderboard

from .utils import cached_property, import_string

class ActivityFeed(object):
    def __init__(self, redis='redis://:@localhost:6379/0', item_loader=None,
            items_loader=None, namespace='activity_feed', aggregate=False,
            aggregate_key='aggregate', page_size=25, connection=None):

        self._redis = connection
        self._redis_url = redis
        self._resolve_item_loaders(item_loader, items_loader)
        self.namespace = namespace
        self.aggregate = aggregate
        self.aggregate_key = aggregate_key
        self.page_size = page_size
        self.members_only = True

    def _resolve_item_loaders(self, item_loader=None, items_loader=None):
        '''Sets the item loader callback functions.'''
        def resolve_loader(loader):
            if isinstance(loader, basestring):
                return import_string(loader)
            if callable(loader):
                return loader
            else:
                return None

        self.items_loader = resolve_loader(items_loader)
        item_loader = resolve_loader(item_loader)

        if not self.items_loader and item_loader:
            self.items_loader = lambda res: [item_loader(v) for v in res]

    @cached_property
    def redis(self):
        if not self._redis:
            self._redis = redis.StrictRedis.from_url(self._redis_url)

        return self._redis

    def _parse_feed_response(self, res):
        if self.members_only:
            items = [v['member'] for v in res]

            if self.items_loader:
                return self.items_loader(items)

            return items

        feed = []
        for o in res:
            if self.item_loader:
                item = self.item_loader(o['member'])
            else:
                item = o['member']

            if not item is None:
                feed.append(item)

        return feed

    def feed(self, user_id, page, aggregate=None):
        """Retrieve a page from the activity feed for a given `user_id`. You
        can configure `ActivityFeed.item_loader` with a Proc to retrieve an
        item from, for example, your ORM (e.g. ActiveRecord) or your ODM (e.g.
        Mongoid), and have the page returned with loaded items rather than item
        IDs.

        :param user_id: [string] User ID.
        :param page: [int] Page in the feed to be retrieved.
        :param aggregate: [boolean, False] Whether to retrieve
                          the aggregate feed for `user_id`.

        @return page from the activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feederboard = self.feederboard_for(user_id, aggregate)
        res = feederboard.leaders(page, page_size=self.page_size, members_only=self.members_only)
        return self._parse_feed_response(res)

    def full_feed(self, user_id, aggregate=None):
        """Retrieve the entire activity feed for a given `user_id`. You can configure
        `ActivityFeed.item_loader` with a Proc to retrieve an item from, for example,
        your ORM (e.g. ActiveRecord) or your ODM (e.g. Mongoid), and have the page
        returned with loaded items rather than item IDs.

        :param user_id: [string] User ID.
        :param aggregate: [boolean, False] Whether to retrieve the aggregate
                          feed for `user_id`.

        @return the full activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feederboard = self.feederboard_for(user_id, aggregate)
        res = feederboard.leaders(1, page_size=feederboard.total_members(), members_only=self.members_only)
        return self._parse_feed_response(res)

    def feed_between_timestamps(self, user_id, starting_timestamp,
            ending_timestamp, aggregate=None):
        """Retrieve a page from the activity feed for a given `user_id` between a
        `starting_timestamp` and an `ending_timestamp`. You can configure
        `ActivityFeed.item_loader` with a Proc to retrieve an item from, for
        example, your ORM (e.g. ActiveRecord) or your ODM (e.g. Mongoid), and
        have the feed data returned with loaded items rather than item IDs.

        :param user_id: [string] User ID.
        :param starting_timestamp: [int] Starting timestamp between which items
                                   in the feed are to be retrieved.
        :param ending_timestamp: [int] Ending timestamp between which items in
                                 the feed are to be retrieved.
         :param aggregate: [boolean, False] Whether to retrieve items from the
                           aggregate feed for `user_id`.

        :return feed items from the activity feed for a given `user_id` between
                the `starting_timestamp` and `ending_timestamp`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feederboard = self.feederboard_for(user_id, aggregate)
        res = feederboard.members_from_score_range(starting_timestamp, ending_timestamp, members_only=self.members_only)
        return self._parse_feed_response(res)

    def total_pages_in_feed(self, user_id, aggregate = None, page_size = None):
        """Return the total number of pages in the activity feed.

        :param user_id: [string] User ID.
        :param aggregate: [boolean, False] Whether to check the total number of
                          pages in the aggregate activity feed or not.
        :param page_size: [int, ActivityFeed.page_size] Page size to be used in
                          calculating the total number of pages in the activity
                          feed.

        :return the total number of pages in the activity feed.
        """
        if aggregate is None:
            aggregate = self.aggregate

        if page_size is None:
            page_size = self.page_size

        feed = self.feederboard_for(user_id, aggregate)
        return feed.total_pages_in(self.feed_key(user_id, aggregate), page_size)

    total_pages = total_pages_in_feed

    def total_items_in_feed(self, user_id, aggregate = None):
        """Return the total number of items in the activity feed.

        :param user_id: [string] User ID.
        :param aggregate: [boolean, False] Whether to check the total number of
                          items in the aggregate activity feed or not.

        @return the total number of items in the activity feed.
        """
        if aggregate is None:
            aggregate = self.aggregate

        return self.feederboard_for(user_id, aggregate).total_members()

    total_items = total_items_in_feed

    def remove_feeds(self, user_id):
        """Remove the activity feeds for a given `user_id`.

        :param user_id [string] User ID.
        """
        pipe = self.redis.pipeline()
        pipe.multi()
        pipe.delete(self.feed_key(user_id, False))
        pipe.delete(self.feed_key(user_id, True))
        pipe.execute()

    def trim_feed(self, user_id, starting_timestamp, ending_timestamp,
            aggregate = None):
        """Trim an activity feed between two timestamps.

        :param user_id: [string] User ID.
        :param starting_timestamp: [int] Starting timestamp after which
                                   activity feed items will be cut.
        :param ending_timestamp: [int] Ending timestamp before which activity
                                 feed items will be cut.
        :param aggregate: [boolean, False] Whether or not to trim the aggregate
                          activity feed or not.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feed = self.feederboard_for(user_id, aggregate)
        feed.remove_members_in_score_range(starting_timestamp, ending_timestamp)

    def expire_feed(self, user_id, seconds, aggregate = None):
        """Expire an activity feed after a set number of seconds.

        :param user_id: [string] User ID.
        :param seconds: [int] Number of seconds after which the activity feed
                        will be expired.
        :param aggregate: [boolean, False] Whether or not to expire the
                          aggregate activity feed or not.
        """
        if aggregate is None:
            aggregate = self.aggregate

        self.redis.expire(self.feed_key(user_id, aggregate), seconds)

    def expire_feed_at(self, user_id, timestamp, aggregate=None):
        """Expire an activity feed at a given timestamp.

        :param user_id: [string] User ID.
        :param timestamp: [int] Timestamp after which the activity feed will be
                          expired.
        :param aggregate: [boolean, False] Whether or not to expire the
                          aggregate activity feed or not.
        """
        if aggregate is None:
            aggregate = self.aggregate

        self.redis.expireat(self.feed_key(user_id, aggregate), timestamp)

    def update_item(self, user_id, item_id, timestamp, aggregate=None):
        """Add or update an item in the activity feed for a given `user_id`.

        :param user_id: [string] User ID.
        :param item_id: [string] Item ID.
        :param timestamp: [int] Timestamp for the item being added or updated.
        :param aggregate: [boolean, False] Whether to add or update the item in
                          the aggregate feed for `user_id`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feederboard = self.feederboard_for(user_id, False)
        feederboard.rank_member(item_id, timestamp)

        if aggregate:
            feederboard = self.feederboard_for(user_id, True)
            feederboard.rank_member(item_id, timestamp)

    add_item = update_item

    def aggregate_item(self, user_id, item_id, timestamp):
        """Specifically aggregate an item in the activity feed for a given `user_id`.
        This is useful if you are going to background the process of populating
        a user's activity feed from friend's activities.

        :param user_id: [string] User ID.
        :param item_id: [string] Item ID.
        :param timestamp: [int] Timestamp for the item being added or updated.
        """
        feederboard = self.feederboard_for(user_id, True)
        feederboard.rank_member(item_id, timestamp)

    def remove_item(self, user_id, item_id):
        """Remove an item from the activity feed for a given `user_id`. This
        will also remove the item from the aggregate activity feed for the
        user.

        :param user_id: [string] User ID.
        :param item_id: [string] Item ID.
        """
        feederboard = self.feederboard_for(user_id, False)
        feederboard.remove_member(item_id)
        feederboard = self.feederboard_for(user_id, True)
        feederboard.remove_member(item_id)

    def check_item(self, user_id, item_id, aggregate = None):
        """Check to see if an item is in the activity feed for a given `user_id`.

        :param user_id [string] User ID.
        :param item_id [string] Item ID.
        :param aggregate [boolean, False] Whether or not to check the aggregate
                         activity feed.
        """
        if aggregate is None:
            aggregate = self.aggregate

        if aggregate:
            feederboard_aggregate = self.feederboard_for(user_id, True)
            return feederboard_aggregate.check_member(item_id)

        feederboard_individual = self.feederboard_for(user_id, False)
        return feederboard_individual.check_member(item_id)

    def feed_key(self, user_id, aggregate=None):
        """Feed key for a `user_id` composed of:

        Feed: `namespace:user_id`
        Aggregate feed: `namespace`:`aggregate_key`:`user_id`

        @return feed key.
        """
        if aggregate is None:
            aggregate = self.aggregate

        if aggregate:
            return "{}:{}:{}".format(self.namespace, self.aggregate_key, user_id)

        return "{}:{}".format(self.namespace, user_id)

    def feederboard_for(self, user_id, aggregate=None):
        """Retrieve a reference to the activity feed for a given `user_id`.

        :param user_id: [string] User ID.
        :param aggregate: [boolean, False] Whether to retrieve the aggregate
                          feed for `user_id` or not.

        @return reference to the activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        return leaderboard.Leaderboard(self.feed_key(user_id, aggregate),
            connection_pool=self.redis.connection_pool)