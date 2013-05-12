import argparse
import pycallgraph
import cProfile
import pstats
from activity import Activity
from activity.utils import datetime_to_timestamp, utcnow, s

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

items = {}

def example_setup():
    a = Activity(
        redis='redis://:@localhost:6379/15',
        item_loader=get_item,
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

def example_run(a):
    for i in range(1, 1200):
        a.feed('foo', 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='example program')
    parser.add_argument('--profile', action='store_true', help='run profiler')
    parser.add_argument('--graph', action='store_true', help='run graph')

    args = parser.parse_args()
    a = example_setup()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    if args.graph:
        pycallgraph.start_trace()

    example_run(a)

    if args.graph:
        pycallgraph.make_dot_graph('example.png')

    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr)
        sort_by = 'cumulative'
        ps.strip_dirs().sort_stats(sort_by).print_stats()

#for item in a.feed('foo', 1, True):
#    print item
