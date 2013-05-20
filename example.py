# -*- coding: utf-8 -*-
import argparse
import cProfile
import pstats
import pycallgraph
import timeit
import time

from activity_feed import ActivityFeed
from activity_feed.utils import datetime_to_timestamp, utcnow

def timestamp_utcnow():
    return datetime_to_timestamp(utcnow())

def _empty(a):
    keys = a.redis.keys('{}*'.format(a.namespace))

    if keys:
        a.redis.delete(*keys)

def create_item(a, user_id, item_id, timestamp):
    item_id = str(item_id)
    items[item_id] = {
        'user_id': user_id,
        'created': timestamp,
        'item_id': item_id}
    a.add_item(user_id, item_id, timestamp)

def get_item(item_id):
    return items[str(item_id)]

def items_loader(res):
    items = [get_item(v) for v in res]
    time.sleep(0.002)
    return items

items = {}

def example_setup():
    global a
    a = ActivityFeed(
        redis='redis://:@localhost:6379/15',
        items_loader=items_loader,
        aggregate=True)

    _empty(a)

    now = timestamp_utcnow()

    for i in range(1, 1200, 2):
        create_item(a, 'foo', i, now)
        now += 5
        create_item(a, 'bar', i+1, now)
        a.aggregate_item('foo', i+1, now)
        now += 5

    return a

def example_run():
    for i in range(1, 1200):
        a.feed('foo', 1)

def example_timeit_run():
    a.feed('foo', 1)

def format_time(seconds):
    v = seconds

    if v * 1000 * 1000 * 1000 < 1000:
        scale = u'ns'
        v = int(round(v*1000*1000*1000))
    elif v * 1000 * 1000 < 1000:
        scale = u'µs'
        v = int(round(v*1000*1000))
    elif v * 1000 < 1000:
        scale = u'ms'
        v = int(round(v*1000))
    else:
        scale = u'sec'
        v = int(v)

    return u'{} {}'.format(v, scale)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='example program')
    parser.add_argument('--profile', action='store_true', help='run profiler')
    parser.add_argument('--graph', action='store_true', help='run graph')
    parser.add_argument('--timeit', type=int, default=0, help='run benchmark')

    args = parser.parse_args()
    a = example_setup()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    if args.graph:
        pycallgraph.start_trace()

    if args.timeit:
        number = args.timeit
        res = timeit.Timer(example_timeit_run).repeat(7, number)
        min_run = min(res)
        per_loop = min_run/number
        print u'{} total run'.format(format_time(min_run))
        print u'{} per/loop'.format(format_time(per_loop))
    else:
        example_run()

    if args.graph:
        pycallgraph.make_dot_graph('example.png')

    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr)
        sort_by = 'cumulative'
        ps.strip_dirs().sort_stats(sort_by).print_stats()

#for item in a.feed('foo', 1, True):
#    print item
