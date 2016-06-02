# -*- coding: utf-8 -*-
from __future__ import absolute_import

from leaderboard.leaderboard import Leaderboard

try:
    from ._utils_speedups import isiterable
except ImportError:
    from .utils import isiterable

from .utils import import_string, cached_property
from .connection import redis_from_url

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
            self._redis = redis_from_url(self._redis_url)

        return self._redis

    def _parse_feed_response(self, res):
        items = [v['member'] for v in res]

        if self.items_loader:
            return self.items_loader(items)

        return items

    def feed(self, user_id, page, aggregate=None, page_size=None):
        """Retrieve a page from the activity feed for a given `user_id`. You
        can configure `ActivityFeed.item_loader` with a Proc to retrieve an
        item from, for example, your ORM (e.g. ActiveRecord) or your ODM (e.g.
        Mongoid), and have the page returned with loaded items rather than item
        IDs.

        :param user_id: [string] User ID.
        :param page: [int] Page in the feed to be retrieved.
        :param aggregate: [boolean, False] Whether to retrieve
                          the aggregate feed for `user_id`.
        :param page_size: [int, None] Page size to be used in fetching the
                          activity feed. If None default page for this object
                          will be used.

        @return page from the activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feederboard = self.feederboard_for(user_id, aggregate)
        res = feederboard.leaders(page, page_size=page_size or self.page_size,
            members_only=True)
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
        res = feederboard.leaders(1, page_size=feederboard.total_members(),
            members_only=True)
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
        res = feederboard.members_from_score_range(starting_timestamp,
                ending_timestamp, members_only=True)
        return self._parse_feed_response(res)

    between = feed_between_timestamps

    def total_pages_in_feed(self, user_id, aggregate=None, page_size=None):
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

        feed = self.feederboard_for(user_id, aggregate)
        return feed.total_pages_in(self.feed_key(user_id, aggregate),
            page_size or self.page_size)

    total_pages = total_pages_in_feed

    def total_items_in_feed(self, user_id, aggregate=None):
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

    trim = trim_feed

    def trim_feed_to_size(self, user_id, size, aggregate=None):
        """Trim an activity down to a certain size

        :param user_id: [string] User ID.
        :param size: [int] size of the feed we want to keep.
        :param aggregate: [boolean, False] Whether or not to trim the aggregate
                          activity feed or not.
        """
        if aggregate is None:
            aggregate = self.aggregate

        feed = self.feederboard_for(user_id, aggregate)
        return feed.remove_members_outside_rank(size)

    def expire_feed(self, user_id, seconds, aggregate=None):
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

    expire_in = expire_feed
    expire_feed_in = expire_feed

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

    expire_at = expire_feed_at

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

        if aggregate:
            pipe = self.redis.pipeline()
            pipe.zadd(self.feed_key(user_id, False), timestamp, item_id)
            pipe.zadd(self.feed_key(user_id, True), timestamp, item_id)
            pipe.execute()
        else:
            self.redis.zadd(self.feed_key(user_id), timestamp, item_id)

    add_item = update_item

    def aggregate_item(self, user_id, item_id, timestamp):
        """Specifically aggregate an item in the activity feed for a given `user_id`.
        This is useful if you are going to background the process of populating
        a user's activity feed from friend's activities.

        :param user_id: [string] User ID or an iterable of User IDs
        :param item_id: [string] Item ID.
        :param timestamp: [int] Timestamp for the item being added or updated.
        """
        if isiterable(user_id):
            pipeline = self.redis.pipeline()

            for uid in user_id:
                pipeline.zadd(self.feed_key(uid, True), timestamp, item_id)

            pipeline.execute()
        else:
            self.redis.zadd(self.feed_key(user_id, True), timestamp, item_id)

    def remove_item(self, user_id, item_id):
        """Remove an item from the activity feed for a given `user_id`. This
        will also remove the item from the aggregate activity feed for the
        user.

        :param user_id: [string] User ID.
        :param item_id: [string] Item ID or an iterable of Item ID's.
        """
        # TODO: Optimize removing many members
        if not isiterable(item_id):
            item_id = (item_id,)

        for _id in item_id:
            feederboard = self.feederboard_for(user_id, False)
            feederboard.remove_member(_id)
            feederboard = self.feederboard_for(user_id, True)
            feederboard.remove_member(_id)

    def check_item(self, user_id, item_id, aggregate=None):
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

        return Leaderboard(self.feed_key(user_id, aggregate),
            connection_pool=self.redis.connection_pool)
