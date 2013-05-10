# -*- coding: utf-8 -*-
from __future__ import absolute_import

import redis
import leaderboard

from .config import Config
from .utils import get_root_path, cached_property

class Activity(object):
    default_config = dict(
        REDIS = 'redis://:@localhost:6379/0',
        ITEM_LOADER = None,
        NAMESPACE = 'activity_feed',
        AGGREGATE = False,
        AGGREGATE_KEY = 'aggregate',
        PAGE_SIZE = 25,
    )

    def __init__(self, import_name=None, redis_client=None):
        self.import_name = import_name or __name__
        self.root_path = get_root_path(self.import_name)
        self.config = Config(self.root_path, self.default_config)
        self._redis = redis_client

    @cached_property
    def redis(self):
        if not self._redis:
            self._redis = redis.StrictRedis.from_url(self.config['REDIS'])

        return self._redis

    def feed(self, user_id, page, aggregate = None):
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
            aggregate = self.config['AGGREGATE']

#feederboard = ActivityFeed.feederboard_for(user_id, aggregate)
#  feed = feederboard.leaders(page, :page_size => ActivityFeed.page_size).inject([]) do |feed_items, feed_item|
#    item = if ActivityFeed.item_loader
#      ActivityFeed.item_loader.call(feed_item[:member])
#    else
#      feed_item[:member]
#    end
#
#    feed_items << item unless item.nil?
#    feed_items
#  end
#
#  feed.nil? ? [] : feed


    def full_feed(self, user_id, aggregate = None):
        """Retrieve the entire activity feed for a given `user_id`. You can configure
        `ActivityFeed.item_loader` with a Proc to retrieve an item from, for example,
        your ORM (e.g. ActiveRecord) or your ODM (e.g. Mongoid), and have the page
        returned with loaded items rather than item IDs.

        :param user_id: [String] User ID.
        :param aggregate: [boolean, False] Whether to retrieve the aggregate feed for `user_id`.

        @return the full activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

  #feederboard = ActivityFeed.feederboard_for(user_id, aggregate)
  #feed = feederboard.leaders(1, :page_size => feederboard.total_members).inject([]) do |feed_items, feed_item|
  #  item = if ActivityFeed.item_loader
  #    ActivityFeed.item_loader.call(feed_item[:member])
  #  else
  #    feed_item[:member]
  #  end

  #  feed_items << item unless item.nil?
  #  feed_items
  #end

  #feed.nil? ? [] : feed

    def feed_between_timestamps(self, user_id, starting_timestamp,
            ending_timestamp, aggregate = None):
        """Retrieve a page from the activity feed for a given `user_id` between a
        `starting_timestamp` and an `ending_timestamp`. You can configure
        `ActivityFeed.item_loader` with a Proc to retrieve an item from, for
        example, your ORM (e.g. ActiveRecord) or your ODM (e.g. Mongoid), and
        have the feed data returned with loaded items rather than item IDs.

        :param user_id: [String] User ID.
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
            aggregate = self.config['AGGREGATE']

      #feederboard = ActivityFeed.feederboard_for(user_id, aggregate)
      #feed = feederboard.members_from_score_range(starting_timestamp, ending_timestamp).inject([]) do |feed_items, feed_item|
      #  item = if ActivityFeed.item_loader
      #    ActivityFeed.item_loader.call(feed_item[:member])
      #  else
      #    feed_item[:member]
      #  end

      #  feed_items << item unless item.nil?
      #  feed_items
      #end

      #feed.nil? ? [] : feed

    def total_pages_in_feed(self, user_id, aggregate = None, page_size = None):
        """Return the total number of pages in the activity feed.

        :param user_id: [String] User ID.
        :param aggregate: [boolean, False] Whether to check the total number of pages in the aggregate activity feed or not.
        :param page_size: [int, ActivityFeed.page_size] Page size to be used in calculating the total number of pages in the activity feed.

        :return the total number of pages in the activity feed.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

        if page_size is None:
            page_size = self.page_size
      #ActivityFeed.feederboard_for(user_id, aggregate).total_pages_in(ActivityFeed.feed_key(user_id, aggregate), page_size)

    total_pages = total_pages_in_feed

    def total_items_in_feed(self, user_id, aggregate = None):
        """Return the total number of items in the activity feed.

        @param user_id [String] User ID.
        @param aggregate [boolean, False] Whether to check the total number of items in the aggregate activity feed or not.

        @return the total number of items in the activity feed.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

      #ActivityFeed.feederboard_for(user_id, aggregate).total_members

    total_items = total_items_in_feed

    def remove_feeds(self, user_id):
        """Remove the activity feeds for a given `user_id`.

        :param user_id [String] User ID.
        """
      #ActivityFeed.redis.multi do |transaction|
      #  transaction.del(ActivityFeed.feed_key(user_id, False))
      #  transaction.del(ActivityFeed.feed_key(user_id, True))
      #end


    def trim_feed(self, user_id, starting_timestamp, ending_timestamp,
            aggregate = None):
        """Trim an activity feed between two timestamps.

        :param user_id: [String] User ID.
        :param starting_timestamp: [int] Starting timestamp after which activity feed items will be cut.
        :param ending_timestamp: [int] Ending timestamp before which activity feed items will be cut.
        :param aggregate: [boolean, False] Whether or not to trim the aggregate activity feed or not.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

        #ActivityFeed.feederboard_for(user_id, aggregate).remove_members_in_score_range(starting_timestamp, ending_timestamp)


    def expire_feed(self, user_id, seconds, aggregate = None):
        """Expire an activity feed after a set number of seconds.

        :param user_id: [String] User ID.
        :param seconds: [int] Number of seconds after which the activity feed will be expired.
        :param aggregate: [boolean, False] Whether or not to expire the aggregate activity feed or not.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

        #ActivityFeed.redis.expire(ActivityFeed.feed_key(user_id, aggregate), seconds)

    def expire_feed_at(self, user_id, timestamp, aggregate=None):
        """Expire an activity feed at a given timestamp.

        :param user_id: [String] User ID.
        :param timestamp: [int] Timestamp after which the activity feed will be
                          expired.
        :param aggregate: [boolean, False] Whether or not to expire the
                          aggregate activity feed or not.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

        self.redis.expireat(self.feed_key(user_id, aggregate), timestamp)

    def update_item(self, user_id, item_id, timestamp, aggregate=None):
        """Add or update an item in the activity feed for a given `user_id`.

        :param user_id: [String] User ID.
        :param item_id: [String] Item ID.
        :param timestamp: [int] Timestamp for the item being added or updated.
        :param aggregate: [boolean, False] Whether to add or update the item in the aggregate feed for `user_id`.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

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

        :param user_id: [String] User ID.
        :param item_id: [String] Item ID.
        :param timestamp: [int] Timestamp for the item being added or updated.
        """
        feederboard = self.feederboard_for(user_id, True)
        feederboard.rank_member(item_id, timestamp)

    def remove_item(self, user_id, item_id):
        """Remove an item from the activity feed for a given `user_id`. This
        will also remove the item from the aggregate activity feed for the
        user.

        :param user_id: [String] User ID.
        :param item_id: [String] Item ID.
        """
        feederboard = self.feederboard_for(user_id, False)
        feederboard.remove_member(item_id)
        feederboard = self.feederboard_for(user_id, True)
        feederboard.remove_member(item_id)

    def check_item(self, user_id, item_id, aggregate = None):
        """Check to see if an item is in the activity feed for a given `user_id`.

        :param user_id [String] User ID.
        :param item_id [String] Item ID.
        :param aggregate [boolean, False] Whether or not to check the aggregate activity feed.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

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
            aggregate = self.config['AGGREGATE']

        namespace = self.config['NAMESPACE']
        aggregate_key = self.config['AGGREGATE_KEY']

        if aggregate:
            return "{}:{}:{}".format(namespace, aggregate_key, user_id)

        return "{}:{}".format(namespace, user_id)

    def feederboard_for(self, user_id, aggregate=None):
        """Retrieve a reference to the activity feed for a given `user_id`.

        :param user_id: [String] User ID.
        :param aggregate: [boolean, False] Whether to retrieve the aggregate feed for `user_id` or not.

        @return reference to the activity feed for a given `user_id`.
        """
        if aggregate is None:
            aggregate = self.config['AGGREGATE']

        return leaderboard.Leaderboard(self.feed_key(user_id, aggregate),
            connection=self.redis)
