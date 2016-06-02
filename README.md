[![Build Status](https://travis-ci.org/simonz05/activity-feed.png?branch=master)](https://travis-ci.org/simonz05/activity-feed)
# ActivityFeed

Activity feeds backed by Redis. Activity feeds may also be
referred to as timelines or news feeds.

port of https://github.com/agoragames/activity_feed

TODO:

- Add missing tests.
    + item_loader
    + configuration

## Installation

ActivityFeed requires a Redis server. See
[Redis's quickstart](http://redis.io/topics/quickstart) for
installation instructions.

To install ActivityFeed:

`$ pip install activity-feed`

## Usage

Import the ActivityFeed library:

`from activity_feed import ActivityFeed`

Create an instance of `ActivityFeed` and add a few items to
foo's activity feed.

```python
activity_feed = ActivityFeed()
timestamp = 1368476968
activity_feed.add_item('foo', 'item-1', timestamp)
activity_feed.add_item('foo', 'item-2', timestamp + 5)
activity_feed.add_item('foo', 'item-3', timestamp + 10)
```

To view foo's feed we can call the `feed()` method.

```python
print activity_feed.feed('foo', 1)
# ['item-3', 'item-2', 'item-1']
```

## ActivityFeed method summary

```ruby
# Item-related

ActivityFeed.update_item(user_id, item_id, timestamp, aggregate=None)
ActivityFeed.add_item(user_id, item_id, timestamp, aggregate=None)

ActivityFeed.aggregate_item(user_id, item_id, timestamp)
ActivityFeed.remove_item(user_id, item_id)
ActivityFeed.check_item(user_id, item_id, aggregate=None)

# Feed-related

ActivityFeed.feed(user_id, page, aggregate=None)
ActivityFeed.full_feed(user_id, aggregate=None)

ActivityFeed.feed_between_timestamps(user_id, starting_timestamp, ending_timestamp, aggregate=None)
ActivityFeed.between(user_id, starting_timestamp, ending_timestamp, aggregate=None)

ActivityFeed.total_pages_in_feed(user_id, aggregate=None, page_size=None)
ActivityFeed.total_pages(user_id, aggregate=None, page_size=None)

ActivityFeed.total_items_in_feed(user_id, aggregate=None)
ActivityFeed.total_items(user_id, aggregate=None)

ActivityFeed.trim_feed(user_id, starting_timestamp, ending_timestamp, aggregate=None)
ActivityFeed.trim(user_id, starting_timestamp, ending_timestamp, aggregate=None)

ActivityFeed.expire_feed(user_id, seconds, aggregate=None)
ActivityFeed.expire_feed_in(user_id, seconds, aggregate=None)
ActivityFeed.expire_in(user_id, seconds, aggregate=None)

ActivityFeed.expire_feed_at(user_id, timestamp, aggregate=None)
ActivityFeed.expire_at(user_id, timestamp, aggregate=None)

ActivityFeed.remove_feeds(user_id)
```

## Copyright

Copyright (c) 2011-2014 David Czarnecki. Copyright (c) 2013-2014 Simon Zimmermann.

See LICENSE for further details.