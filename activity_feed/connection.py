import urlparse
import redis

try:
    import pack_command

    class Connection(redis.Connection):
        pack_command = pack_command.pack_command
except ImportError:
    Connection = redis.Connection

def redis_from_url(url, db=None, charset='utf-8', errors='strict',
        decode_responses=False, socket_timeout=None, **kwargs):
    """Return a Redis client object configured from the given URL.

    For example::

        redis://username:password@localhost:6379/0

    If ``db`` is None, this method will attempt to extract the database ID
    from the URL path component.

    Any additional keyword arguments will be passed along to the Redis
    class's initializer.
    """
    url = urlparse.urlparse(url)

    # We only support redis:// schemes.
    assert url.scheme == 'redis' or not url.scheme

    # Extract the database ID from the path component if hasn't been given.
    if db is None:
        try:
            db = int(url.path.replace('/', ''))
        except (AttributeError, ValueError):
            db = 0

    # TODO: unix domain sockets
    pool = redis.ConnectionPool(connection_class=Connection,
        host=url.hostname, port=int(url.port or 6379), db=db,
        password=url.password, decode_responses=decode_responses,
        encoding=charset, encoding_errors=errors,
        socket_timeout=socket_timeout)

    return redis.StrictRedis(connection_pool=pool, **kwargs)
