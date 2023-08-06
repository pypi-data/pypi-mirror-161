import datetime
import pytz
import uuid
import json
import time
import hashlib
from redis.exceptions import TimeoutError, ConnectionError
from contextlib import ExitStack
from inspect import signature

from python_grains.utils import chunker
from python_grains.locks import Lock, LockError
from python_grains.queues.lua import LuaScripts

DATA_IDX_KEY = 'i'
DATA_TIME_KEY = 't'
DATA_DATA_KEY = 'd'
DATA_MAX_RETRY_KEY = 'm'
HASH_EVENT_PREFIX = 'e'

DEFAULT_QUEUE_TTL = 24 * 60 * 60
DEFAULT_PROCESSING_QUEUE_TTL = 60 * 60
DEFAULT_LOCK_TTL = 10
DEFAULT_MAX_RETRY = 1

class QueueError(Exception): pass

class Event(object):

    data_idx_key = DATA_IDX_KEY
    data_time_key = DATA_TIME_KEY
    data_data_key = DATA_DATA_KEY
    data_max_retry_key = DATA_MAX_RETRY_KEY
    default_lock_ttl = DEFAULT_LOCK_TTL

    def __init__(self,
                 data,
                 redis_client,
                 timestamp=None,
                 idx=None,
                 lock_ttl=None,
                 processing_queue_key=None,
                 max_retry=DEFAULT_MAX_RETRY):

        self.data = data
        self.datetime = self.datetime_from_utctimestamp(timestamp) or self.utcnow()
        self.idx = idx or self.new_idx()
        self.redis_client = redis_client
        self.lock_ttl = lock_ttl or self.default_lock_ttl
        self.processing_queue_key = processing_queue_key
        self.max_retry = max_retry

        self.processed = False
        self.n_try = 0
        self.success = False
        self.result = None

    @staticmethod
    def datetime_from_utctimestamp(timestamp):

        if timestamp is None:
            return None
        return pytz.utc.localize(datetime.datetime.utcfromtimestamp(timestamp))

    @staticmethod
    def utcnow():

        return pytz.utc.localize(datetime.datetime.utcnow())

    @staticmethod
    def new_idx():

        return str(uuid.uuid4())

    def lock(self):

        return Lock(idx=self.lock_idx,
                    conn=self.redis_client,
                    ttl=self.lock_ttl * 1000)

    def delete(self, pipe=None):
        if pipe:
            pipe.hdel(self.processing_queue_key,
                      self.try_count_key,
                      self.result_key)
        else:
            self.redis_client.hdel(self.processing_queue_key,
                                   self.try_count_key,
                                   self.result_key)

    def store_result(self, result, pipe=None):

        assert isinstance(result, str), 'result should be a string'

        if pipe:
            pipe.hset(self.processing_queue_key,
                                   self.result_key,
                                   result)
        else:
            self.redis_client.hset(self.processing_queue_key,
                                   self.result_key,
                                   result)


    def reset_try_count(self):

        self.redis_client.hdel(self.processing_queue_key,
                               self.try_count_key)

    def incr_try_count(self, pipe=None):

        if self.processing_queue_key is None:
            raise QueueError('No processing queue key given')

        if pipe:
            pipe.hincrby(self.processing_queue_key,
                                      self.try_count_key,
                                      amount=1)
        else:
            self.redis_client.hincrby(self.processing_queue_key,
                                      self.try_count_key,
                                      amount=1)

    @property
    def max_tries_reached(self):

        return self.try_count >= self.max_retry + 1

    @property
    def prev_result(self):
        result = self.redis_client.hget(self.processing_queue_key,
                                        self.result_key)
        return result.decode() if isinstance(result, bytes) else result

    @property
    def try_count(self):

        if self.processing_queue_key is None:
            raise QueueError('No processing queue key given')

        count = self.redis_client.hget(self.processing_queue_key,
                                       self.try_count_key)
        if count is None:
            return 0

        return int(count)

    @classmethod
    def from_redis_string(cls,
                          raw_string,
                          redis_client,
                          processing_queue_key=None):

        raw_string = raw_string.decode() if isinstance(raw_string, bytes) else raw_string
        data = json.loads(raw_string)
        return cls(data=data[cls.data_data_key],
                   timestamp=data[cls.data_time_key],
                   idx=data[cls.data_idx_key],
                   max_retry=data[cls.data_max_retry_key],
                   redis_client=redis_client,
                   processing_queue_key=processing_queue_key)

    @property
    def score(self):

        return self.datetime.timestamp()

    @property
    def event_data(self):

        return {
            self.data_idx_key: self.idx,
            self.data_time_key: self.score,
            self.data_data_key: self.data,
            self.data_max_retry_key: self.max_retry
        }

    @property
    def datastring(self):

        return json.dumps(self.event_data)

    @property
    def mapping(self):

        return {self.datastring: self.score}

    @property
    def lock_idx(self):

        return f'ev:{self.idx}'

    @property
    def redis_version(self):

        if not hasattr(self, '_redis_version'):
            self._redis_version = tuple(int(i) for i in self.redis_client.info()['redis_version'].split('.'))

        return self._redis_version

    @property
    def try_count_key(self):

        return f'rt:{self.idx}'

    @property
    def result_key(self):

        return f'rs:{self.idx}'

    @property
    def _ident(self):
        conn_kwargs = self.redis_client.get_connection_kwargs()
        return f'{conn_kwargs["host"]}:{conn_kwargs["port"]}:{conn_kwargs["db"]}:{self.idx}'

    @property
    def guid(self):
        return hashlib.sha256(self._ident.encode('utf-8')).hexdigest()

class ProcessingQueue(object):

    key_prefix = 'qp'
    default_ttl = DEFAULT_PROCESSING_QUEUE_TTL
    lock_ttl = DEFAULT_LOCK_TTL

    def __init__(self,
                 parent_key,
                 register_key,
                 main_queue_ttl,
                 redis_client,
                 idx=None,
                 ttl=None):

        self.parent_key = parent_key
        self.register_key = register_key
        self.main_queue_ttl = main_queue_ttl
        self.ttl = ttl or self.default_ttl
        self.idx = idx or self.new_idx()
        self.events = None
        self.redis_client = redis_client
        self.add_create_processing_queue_lua()

    def add_create_processing_queue_lua(self):

        if not hasattr(self.redis_client, 'create_processing_queue'):
            self.redis_client.create_processing_queue = self.redis_client.register_script(
                LuaScripts.create_processing_queue(data_idx_key=DATA_IDX_KEY,
                                                   hash_event_prefix=HASH_EVENT_PREFIX,
                                                   legacy=self.redis_version[0] < 4))

    def new_idx(self):

        return str(uuid.uuid4())

    def setup(self,
              max_elements,
              min_ts,
              max_ts):

        result = self.redis_client.create_processing_queue(
            keys=[
                self.parent_key,
                self.queue_key,
                self.register_key
            ],
            args=[
                min_ts,
                max_ts,
                self.main_queue_ttl,
                pytz.utc.localize(datetime.datetime.utcnow()).timestamp(),
                max_elements
            ]
        )
        self.events = [Event.from_redis_string(raw_string=raw_string,
                                               redis_client=self.redis_client,
                                               processing_queue_key=self.queue_key)
                       for raw_string in result]

    def lock(self):

        return Lock(idx=self.lock_idx,
                    conn=self.redis_client,
                    ttl=self.lock_ttl * 1000)

    def delete(self):

        pipe = self.redis_client.pipeline()
        pipe.delete(self.queue_key)
        pipe.zrem(self.register_key, self.queue_key)
        pipe.execute()

    @classmethod
    def get(cls,
            parent_key,
            register_key,
            main_queue_ttl,
            redis_client,
            max_elements,
            min_ts,
            max_ts,
            ttl=None):

        queue = cls(parent_key=parent_key,
                    register_key=register_key,
                    main_queue_ttl=main_queue_ttl,
                    ttl=ttl,
                    redis_client=redis_client)

        queue.setup(min_ts=min_ts,
                    max_ts=max_ts,
                    max_elements=max_elements)

        return queue

    def result_object(self, event_id, success, result, will_retry):

        return {
            'id': event_id,
            'success': success,
            'result': result,
            'retry': will_retry}

    def process(self,
                func):

        n_par = len(signature(func).parameters)
        if n_par == 0 or n_par > 2:
            raise QueueError('processing function should take 1 or 2 arguments')

        results = []

        for event in self.events:
            try:
                with event.lock():
                    if n_par == 1:
                        success, result = func(event.data)
                    else:
                        success, result = func(event.data, event.prev_result)
                    if success:
                        event.delete()
                        will_retry = False
                    else:
                        if not event.max_tries_reached:
                            event.store_result(result=result)
                            event.incr_try_count()
                            will_retry = True
                        else:
                            event.delete()
                            will_retry = False
                    results.append(self.result_object(event_id=event.idx,
                                                      success=success,
                                                      result=result,
                                                      will_retry=will_retry))
            except (LockError, TimeoutError, ConnectionError) as e:
                will_retry = True
                if isinstance(e, LockError):
                    success = None
                    result = 'Lock failed'
                else:
                    success = False
                    result = str(e)
                    event.incr_try_count()
                    if not event.max_tries_reached:
                        event.store_result(result=result)
                        event.incr_try_count()
                    else:
                        event.delete()
                        will_retry = False

                results.append(self.result_object(event_id=event.idx, success=success, result=result, will_retry=will_retry))
                continue

        if all(result['success'] or not result['retry'] for result in results):
            self.delete()

        return results

    def batch_process(self,
                      func,
                      batch_size):

        results = []
        for chunk in chunker(self.events, batch_size):
            try:
                locks = [event.lock() for event in chunk]
                with ExitStack() as stack:
                    for lock in locks:
                        stack.enter_context(lock)
                    _results = func([(event.idx, event.data, event.prev_result) for event in chunk])
                    _event_dict = {event.idx: event for event in chunk}
                    pipe = self.redis_client.pipeline()
                    for r in _results:
                        event_id, success, result = r
                        event = _event_dict[event_id]
                        if success:
                            event.delete(pipe=pipe)
                            will_retry = False
                        else:
                            if not event.max_tries_reached:
                                event.store_result(result=result, pipe=pipe)
                                event.incr_try_count(pipe=pipe)
                                will_retry = True
                            else:
                                event.delete(pipe=pipe)
                                will_retry = False
                        results.append(self.result_object(event_id=event.idx,
                                                          success=success,
                                                          result=result,
                                                          will_retry=will_retry))
                    pipe.execute()


            except (LockError, ConnectionError, TimeoutError) as e:
                will_retry = True
                if isinstance(e, LockError):
                    success = None
                    result = 'Lock failed'
                else:
                    success = False
                    result = str(e)
                results.extend([self.result_object(event_id=event.idx,
                                                   success=success,
                                                   result=result,
                                                   will_retry=will_retry) for event in chunk])
                continue

            if all(result['success'] or not result['retry'] for result in results):
                self.delete()

        return results

    def setup_rogue(self):

        result = self.redis_client.hgetall(self.queue_key)
        if len(result) > 0:
            result_dict = {k.decode() if isinstance(k, bytes) else k: v for k, v in result.items()}
            event_dict = {k: v for k, v in result_dict.items() if k.startswith(HASH_EVENT_PREFIX + ':')}
            self.events = [Event.from_redis_string(raw_string=raw_string,
                                                   redis_client=self.redis_client,
                                                   processing_queue_key=self.queue_key)
                           for raw_string in event_dict.values()]
        else:
            self.events = []

        if len(self.events) > 0:
            self.redis_client.expire(self.queue_key, self.main_queue_ttl)

    @classmethod
    def get_rogue(cls,
                  parent_key,
                  register_key,
                  main_queue_ttl,
                  redis_client,
                  margin=120,
                  offset=0,
                  ttl=None):

        max_ts = pytz.utc.localize(datetime.datetime.utcnow()).timestamp() - margin
        queue_keys = redis_client.zrangebyscore(register_key,
                                                min='-inf',
                                                max=max_ts,
                                                start=offset,
                                                num=1)

        if len(queue_keys) == 0:
            return None

        queue_key = queue_keys[0]
        queue_key = queue_key.decode() if isinstance(queue_key, bytes) else queue_key
        queue_idx = queue_key.split(':')[-1]
        queue = cls(parent_key=parent_key,
                    register_key=register_key,
                    main_queue_ttl=main_queue_ttl,
                    ttl=ttl,
                    idx=queue_idx,
                    redis_client=redis_client)
        queue.setup_rogue()
        return queue

    @property
    def redis_version(self):

        if not hasattr(self, '_redis_version'):
            self._redis_version = tuple(int(i) for i in self.redis_client.info()['redis_version'].split('.'))

        return self._redis_version

    @property
    def len(self):

        return len(self.events)

    @property
    def queue_key(self):

        return f'{self.key_prefix}:{self.idx}'

    @property
    def lock_idx(self):

        return f'pq:{self.idx}'

    @property
    def _ident(self):
        conn_kwargs = self.redis_client.get_connection_kwargs()
        return f'{conn_kwargs["host"]}:{conn_kwargs["port"]}:{conn_kwargs["db"]}:{self.idx}'

    @property
    def guid(self):
        return hashlib.sha256(self._ident.encode('utf-8')).hexdigest()


class Queue(object):

    key_prefix = 'qm'

    def __init__(self,
                 name,
                 ttl,
                 redis_client,
                 max_retry=DEFAULT_MAX_RETRY):

        self.name = name
        self.ttl = ttl
        self.redis_client = redis_client
        self.results = []
        self.add_delete_queue_lua()
        self.max_retry = max_retry

    def push(self,
             *events):

        if not all(isinstance(event, Event) for event in events):
            raise ValueError('all events need to be of type Event')

        mapping = {k: v for event in events for k, v in event.mapping.items()}
        n = self.redis_client.zadd(self.main_key, mapping=mapping, nx=True)
        self.expire()

        return n

    def push_raw(self,
                 *data):

        events = [Event(d, redis_client=self.redis_client, max_retry=self.max_retry) for d in data]
        return self.push(*events)

    def add_delete_queue_lua(self):

        if not hasattr(self.redis_client, 'delete_queue'):
            self.redis_client.delete_queue = self.redis_client.register_script(LuaScripts.delete_queue())

    def delete(self):

        self.redis_client.delete_queue(
            keys=[
                self.main_key,
                self.register_processing_queue_key
            ]
        )

    def expire(self):

        self.redis_client.expire(self.main_key, self.ttl)

    def get_processing_queue(self,
                             max_elements=None,
                             min_ts=None,
                             max_ts=None,
                             ttl=None):

        return ProcessingQueue.get(
            parent_key=self.main_key,
            register_key=self.register_processing_queue_key,
            main_queue_ttl=self.ttl,
            max_elements=max_elements,
            min_ts=min_ts,
            max_ts=max_ts,
            ttl=ttl,
            redis_client=self.redis_client)

    def get_rogue_processing_queue(self,
                                   margin=120,
                                   offset=0,
                                   ttl=None):

        return ProcessingQueue.get_rogue(
            parent_key=self.main_key,
            register_key=self.register_processing_queue_key,
            main_queue_ttl=self.ttl,
            redis_client=self.redis_client,
            margin=margin,
            offset=offset,
            ttl=ttl)

    def process(self,
                func,
                ptime=120,
                chunk_size=50,
                min_ts='-inf',
                max_ts='+inf',
                handle_rogues=True,
                quit_when_empty=True,
                max_rogues=100,
                interval=1):

        # the func should return a tuple (success, result)
        # the success boolean is used to determine if the event was handled successful

        start = time.time()
        if handle_rogues:
            for offset in range(max_rogues):
                pq = self.get_rogue_processing_queue(offset=offset)
                if pq is None:
                    break
                try:
                    with pq.lock():
                        self.results.append(pq.process(func))
                except (LockError, ConnectionError, TimeoutError):
                    continue

        while time.time() - start <= ptime:
            q = self.get_processing_queue(max_elements=chunk_size, min_ts=min_ts, max_ts=max_ts)
            if not q.len == 0:
                try:
                    with q.lock():
                        self.results.append(q.process(func))
                except (LockError, ConnectionError, TimeoutError):
                    continue
            else:
                if quit_when_empty:
                    break
                else:
                    time.sleep(interval)

        return self.results

    def batch_process(self,
                      func,
                      batch_size,
                      ptime=120,
                      chunk_size=50,
                      min_ts=None,
                      max_ts=None,
                      handle_rogues=True,
                      quit_when_empty=False,
                      max_rogues=100,
                      interval=1):

        # the func should return a tuple (event_id, success, result)
        # the success boolean is used to determine if the event was handled successful

        start = time.time()
        if handle_rogues:
            for offset in range(max_rogues):
                pq = self.get_rogue_processing_queue(offset=offset)
                if pq is None:
                    break
                try:
                    with pq.lock():
                        self.results.extend(pq.batch_process(func, batch_size=batch_size))
                except (LockError, ConnectionError, TimeoutError):
                    continue

        while time.time() - start <= ptime:
            q = self.get_processing_queue(max_elements=chunk_size, min_ts=min_ts, max_ts=max_ts)
            if not q.len == 0:
                try:
                    with q.lock():
                        self.results.extend(q.batch_process(func, batch_size=batch_size))
                except (LockError, ConnectionError, TimeoutError):
                    continue
            else:
                if quit_when_empty:
                    break
                else:
                    time.sleep(interval)

        return self.results

    @property
    def len(self):

        return self.redis_client.zcard(self.main_key)

    @property
    def main_key(self):

        return f'{self.key_prefix}:{self.name}'

    @property
    def register_processing_queue_key(self):

        return f'{self.key_prefix}:{self.name}:processing'

    @property
    def redis_version(self):

        if not hasattr(self, '_redis_version'):
            self._redis_version = tuple(int(i) for i in self.redis_client.info()['redis_version'].split('.'))

        return self._redis_version

    @property
    def _ident(self):
        conn_kwargs = self.redis_client.get_connection_kwargs()
        return f'{conn_kwargs["host"]}:{conn_kwargs["port"]}:{conn_kwargs["db"]}:{self.name}'

    @property
    def guid(self):
        return hashlib.sha256(self._ident.encode('utf-8')).hexdigest()
