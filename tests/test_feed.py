# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import leaderboard
from .helper import BaseTest, timestamp

from activity.utils import datetime_to_timestamp

class FeedTest(BaseTest):
    def feed_test(self):
        'should return an activity feed with the items correctly ordered'
        self.add_items_to_feed('david')
        feed = self.a.feed('david', 1)
        self.assertEqual(len(feed), 5)
        self.assertEqual(int(feed[0]), 5)
        self.assertEqual(int(feed[4]), 1)

    def feed_aggregation_test(self):
        'should return an aggregate activity feed with the items correctly ordered'
        self.add_items_to_feed('david', aggregate=True)
        feed = self.a.feed('david', 1, True)
        self.assertEqual(len(feed), 5)
        self.assertEqual(int(feed[0]), 5)
        self.assertEqual(int(feed[4]), 1)

    def full_feed_test(self):
        'should return the full activity feed'
        self.add_items_to_feed('david', 30)

        feed = self.a.full_feed('david', False)
        self.assertEqual(len(feed), 30)
        self.assertEqual(int(feed[0]), 30)
        self.assertEqual(int(feed[29]), 1)

    def full_feed_aggregation_test(self):
        'should return the full activity feed'
        self.add_items_to_feed('david', 30, True)

        feed = self.a.full_feed('david', True)
        self.assertEqual(len(feed), 30)
        self.assertEqual(int(feed[0]), 30)
        self.assertEqual(int(feed[29]), 1)


    def feed_between_timestamps_test(self):
        '''Should return activity feed items between the starting and ending
        timestamps.'''
        self.a.update_item('david', 1, timestamp(2012, 6, 19, 4, 0, 0))
        self.a.update_item('david', 2, timestamp(2012, 6, 19, 4, 30, 0))
        self.a.update_item('david', 3, timestamp(2012, 6, 19, 5, 30, 0))
        self.a.update_item('david', 4, timestamp(2012, 6, 19, 6, 37, 0))
        self.a.update_item('david', 5, timestamp(2012, 6, 19, 8, 17, 0))

        from_t = timestamp(2012, 6, 19, 4, 43, 0)
        to_t = timestamp(2012, 6, 19, 8, 16, 0)
        feed = self.a.feed_between_timestamps('david', from_t, to_t)

        self.assertEqual(len(feed), 2)
        self.assertEqual(int(feed[0]), 4)
        self.assertEqual(int(feed[1]), 3)

    def feed_between_timestamps_aggregation_test(self):
        '''Should return activity feed items between the starting and ending
        timestamps.'''
        self.a.update_item('david', 1, timestamp(2012, 6, 19, 4, 0, 0), True)
        self.a.update_item('david', 2, timestamp(2012, 6, 19, 4, 30, 0), True)
        self.a.update_item('david', 3, timestamp(2012, 6, 19, 5, 30, 0), True)
        self.a.update_item('david', 4, timestamp(2012, 6, 19, 6, 37, 0), True)
        self.a.update_item('david', 5, timestamp(2012, 6, 19, 8, 17, 0), True)

        from_t = timestamp(2012, 6, 19, 4, 43, 0)
        to_t = timestamp(2012, 6, 19, 8, 16, 0)
        feed = self.a.feed_between_timestamps('david', from_t, to_t, True)

        self.assertEqual(len(feed), 2)
        self.assertEqual(int(feed[0]), 4)
        self.assertEqual(int(feed[1]), 3)

    def total_pages_in_feed_test(self):
        'should return the correct number of pages in the activity feed'
        self.add_items_to_feed('david', leaderboard.Leaderboard.DEFAULT_PAGE_SIZE + 1)

        self.assertEqual(self.a.total_pages_in_feed('david'), 2)
        self.assertEqual(self.a.total_pages('david'), 2)

    def total_pages_in_feed_aggregation_test(self):
        'should return the correct number of pages in the aggregate activity feed'
        self.add_items_to_feed('david', leaderboard.Leaderboard.DEFAULT_PAGE_SIZE + 1, True)

        self.assertEqual(self.a.total_pages_in_feed('david', True), 2)
        self.assertEqual(self.a.total_pages('david', True), 2)

    def changing_page_size_parameter_test(self):
        'should return the correct number of pages in the activity feed'
        self.add_items_to_feed('david', 25)

        self.assertEqual(self.a.total_pages_in_feed('david', False, 4), 7)
        self.assertEqual(self.a.total_pages('david', False, 4), 7)

    def remove_feeds_test(self):
        'should remove the activity feeds for a given user ID'
        page_size = leaderboard.Leaderboard.DEFAULT_PAGE_SIZE + 1
        self.add_items_to_feed('david', page_size)

        self.assertEqual(self.a.total_items_in_feed('david'), page_size)
        self.assertEqual(self.a.total_items('david'), page_size)

        self.a.remove_feeds('david')

        self.assertEqual(self.a.total_items_in_feed('david'), 0)
        self.assertEqual(self.a.total_items('david'), 0)

    def total_items_in_feed_test(self):
        'should return the correct number of items in the activity feed'
        page_size = leaderboard.Leaderboard.DEFAULT_PAGE_SIZE + 1
        self.add_items_to_feed('david', page_size)

        self.assertEqual(self.a.total_items_in_feed('david'), page_size)
        self.assertEqual(self.a.total_items('david'), page_size)

    def total_items_in_feed_aggregation_test(self):
        'should return the correct number of items in the aggregate activity feed'
        page_size = leaderboard.Leaderboard.DEFAULT_PAGE_SIZE + 1
        self.add_items_to_feed('david', page_size, True)

        self.assertEqual(self.a.total_items_in_feed('david', True), page_size)
        self.assertEqual(self.a.total_items('david', True), page_size)

    def trim_feed_test(self):
        '''should trim activity feed items between the starting and ending
        timestamps'''
        self.a.update_item('david', 1, timestamp(2012, 6, 19, 4, 0, 0))
        self.a.update_item('david', 2, timestamp(2012, 6, 19, 4, 30, 0))
        self.a.update_item('david', 3, timestamp(2012, 6, 19, 5, 30, 0))
        self.a.update_item('david', 4, timestamp(2012, 6, 19, 6, 37, 0))
        self.a.update_item('david', 5, timestamp(2012, 6, 19, 8, 17, 0))

        self.a.trim_feed('david', timestamp(2012, 6, 19, 4, 29, 0), timestamp(2012, 6, 19, 8, 16, 0))

        feed = self.a.feed('david', 1)
        self.assertEqual(len(feed), 2)
        self.assertEqual(int(feed[0]), 5)
        self.assertEqual(int(feed[1]), 1)

    def trim_feed_aggregation_test(self):
        '''should trim activity feed items between the starting and ending
        timestamps'''
        self.a.update_item('david', 1, timestamp(2012, 6, 19, 4, 0, 0), True)
        self.a.update_item('david', 2, timestamp(2012, 6, 19, 4, 30, 0), True)
        self.a.update_item('david', 3, timestamp(2012, 6, 19, 5, 30, 0), True)
        self.a.update_item('david', 4, timestamp(2012, 6, 19, 6, 37, 0), True)
        self.a.update_item('david', 5, timestamp(2012, 6, 19, 8, 17, 0), True)

        self.a.trim_feed('david', timestamp(2012, 6, 19, 4, 29, 0), timestamp(2012, 6, 19, 8, 16, 0), True)

        feed = self.a.feed('david', 1, True)
        self.assertEqual(len(feed), 2)
        self.assertEqual(int(feed[0]), 5)
        self.assertEqual(int(feed[1]), 1)

    def expire_feed_test(self):
        'should set an expiration on an activity feed'
        self.add_items_to_feed('david', leaderboard.Leaderboard.DEFAULT_PAGE_SIZE)
        self.a.expire_feed('david', 10)
        ttl = self.a.redis.ttl(self.a.feed_key('david'))
        self.assertEqual(1 < ttl <= 10, True)

    def expire_feed_at_test(self):
        'should set an expiration timestamp on an activity feed.'
        self.add_items_to_feed('david', leaderboard.Leaderboard.DEFAULT_PAGE_SIZE)
        t = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.a.expire_feed_at('david', datetime_to_timestamp(t))
        ttl = self.a.redis.ttl(self.a.feed_key('david'))
        self.assertEqual(1 < ttl <= 10, True)

#  describe 'ORM or ODM loading' do
#    describe 'ActiveRecord' do
#      it 'should be able to load an item via ActiveRecord when requesting a feed' do
#        ActivityFeed.item_loader = Proc.new do |id|
#          ActivityFeed::ActiveRecord::Item.find(id)
#        end
#
#        feed = ActivityFeed.feed('david', 1)
#        feed.length.should eql(0)
#
#        item = ActivityFeed::ActiveRecord::Item.create(
#          :user_id => 'david',
#          :nickname => 'David Czarnecki',
#          :type => 'some_activity',
#          :title => 'Great activity',
#          :body => 'This is text for the feed item'
#        )
#
#        feed = ActivityFeed.feed('david', 1)
#        feed.length.should eql(1)
#        feed[0].should == item
#      end
#    end
#
#    describe 'Mongoid' do
#      it 'should be able to load an item via Mongoid when requesting a feed' do
#        ActivityFeed.item_loader = Proc.new { |id| ActivityFeed::Mongoid::Item.find(id) }
#
#        feed = ActivityFeed.feed('david', 1)
#        feed.length.should eql(0)
#
#        item = ActivityFeed::Mongoid::Item.create(
#          :user_id => 'david',
#          :nickname => 'David Czarnecki',
#          :type => 'some_activity',
#          :title => 'Great activity',
#          :text => 'This is text for the feed item',
#          :url => 'http://url.com'
#        )
#
#        feed = ActivityFeed.feed('david', 1)
#        feed.length.should eql(1)
#        feed[0].should == item
#      end
#    end
#  end
#

