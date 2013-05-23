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

Activity requires a Redis server. See
[Redis's quickstart](http://redis.io/topics/quickstart) for
installation instructions.

To install Activity:

`$ pip install Activity`

## Usage

Require the activity library

`from activity import Activity`

Create an instance of Activity and add a few items to 
foo's activity-feed.

```python
a = Activity()
timestamp = 1368476968
a.add_item('foo', 'item-1', timestamp)
a.add_item('foo', 'item-2', timestamp + 5)
a.add_item('foo', 'item-3', timestamp + 10)
```

To view foo's feed we can call the `feed()` method.

```python
print a.feed('foo', 1)
# ['item-3', 'item-2', 'item-1']
```
