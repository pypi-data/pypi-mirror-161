import redis
import uuid
import datetime
import time
import random
from python_grains.utils import RedisClientWithRetry

DEFAULT_RETRY_TIMES = 0
DEFAULT_RETRY_DELAY = 100
LOCK_TTL = 100000 # in milliseconds
CLOCK_DRIFT_FACTOR = 0.01
USER_QUEUE_TTL = 3600 # in seconds
MAX_PROCESSING_RETRIES = 3

RELEASE_LUA = '''
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end'''

class LockError(Exception): pass

class Lock(object):

    def __init__(self, idx, conn, ttl,  # ttl in milliseconds
                 retry_times=DEFAULT_RETRY_TIMES,
                 retry_delay=DEFAULT_RETRY_DELAY):

        self.type = type
        self.lock_id = 'lck:' + idx
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.ttl = ttl

        if not isinstance(conn, (redis.StrictRedis, RedisClientWithRetry)):
            raise LockError('No valid connection details provided')

        self.redis_node = conn
        self.add_release_script()

    def add_release_script(self):
        if not hasattr(self.redis_node, 'release_lock'):
            self.redis_node.release_lock = self.redis_node.register_script(RELEASE_LUA)

    def __enter__(self):
        acquired, validity = self.acquire_with_validity()
        if not acquired:
            raise LockError('Failed to acquire lock.')
        return validity

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def release(self):
        self.release_node(self.redis_node)

    def _total_ms(self, delta):
        """
        Get the total number of milliseconds in a timedelta object with
        microsecond precision.
        """
        delta_seconds = delta.seconds + delta.days * 24 * 3600
        return (delta.microseconds + delta_seconds * 10**6) / 10**3

    def acquire_node(self, node):
        """
        acquire a single redis node
        """
        try:
            return node.set(self.lock_id, self.lock_key, nx=True, px=self.ttl)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return False

    def release_node(self, node):
        """
        release a single redis node
        """
        # use the lua script to release the lock in a safe way
        try:
            node.release_lock(keys=[self.lock_id], args=[self.lock_key])
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            pass

    def locked(self):

        if self.redis_node.get(self.lock_id):
            return True
        return False

    def acquire(self):
        acquired, validity = self._acquire()
        return acquired

    def acquire_with_validity(self):
        return self._acquire()

    def _acquire(self):

        # lock_key should be random and unique
        self.lock_key = uuid.uuid4().hex

        for retry in range(self.retry_times + 1):
            start_time = datetime.datetime.utcnow()

            # acquire the lock
            acquired = self.acquire_node(self.redis_node)

            end_time = datetime.datetime.utcnow()
            elapsed_milliseconds = self._total_ms(end_time - start_time)

            # Add 2 milliseconds to the drift to account for Redis expires
            # precision, which is 1 millisecond, plus 1 millisecond min drift
            # for small TTLs.
            drift = (self.ttl * CLOCK_DRIFT_FACTOR) + 2

            validity = self.ttl - (elapsed_milliseconds + drift)

            if validity > 0 and acquired:
                return True, validity
            else:
                self.release_node(self.redis_node)
                time.sleep(random.randint(0, self.retry_delay) / 1000)

        return False, 0