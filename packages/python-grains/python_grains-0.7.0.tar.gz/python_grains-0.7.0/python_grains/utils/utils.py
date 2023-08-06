import redis
from redis.retry import Retry
from redis.backoff import DecorrelatedJitterBackoff
import socket

class RedisClientWithRetry(object):

    @classmethod
    def from_config(cls, *args, max_retry=5, **kwargs):
        backoff = DecorrelatedJitterBackoff(cap=2.0, base=0.5)
        retry = Retry(retries=max_retry, backoff=backoff)
        redis_client = redis.Redis(*args,
                                   retry_on_error=[redis.exceptions.ConnectionError,
                                                   redis.exceptions.TimeoutError,
                                                   socket.timeout],
                                   retry=retry,
                                   **kwargs)
        return redis_client

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def search_obj_from_array(array, fieldname, fieldvalue):
    _obj = [o for o in array if o.get(fieldname, str(fieldvalue) + 'not_it') == fieldvalue]
    if len(_obj) == 0:
        return None
    return _obj[0]