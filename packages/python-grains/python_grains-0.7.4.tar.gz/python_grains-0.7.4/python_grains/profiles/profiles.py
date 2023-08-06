import datetime
import pytz
import time
import random
import json
import uuid
import functools
import sys
import inspect

from python_grains.profiles import profile_properties
from python_grains.profiles import exceptions
from python_grains.locks import Lock

DEFAULT_DOMAIN = None
DEFAULT_REDIS_CLIENT = None
DEFAULT_DJANGO_PROFILE_MODEL = None
DEFAULT_DJANGO_COUNT_FUNC = None
DEFAULT_DJANGO_POINTER_MODEL = None
DEFAULT_DJANGO_CONNECTION_TUPLE = (None, None)
DEFAULT_PROFILE_TTL = 12 * 60 * 60
DEFAULT_PROFILE_TTL_MARGIN = 2 * 60 * 60
DEFAULT_USER_TTL = 6 * 24 * 60 * 60
DEFAULT_USER_DATA_TTL_MARGIN = 2
DEFAULT_FAST_CLEAN_THRESHOLD = 3
DEFAULT_CLEAN_QUEUE_TTL = 24 * 60 * 60

def set_data_type_properties(cls):

    cls.data_types = {
        prop.py_key: (prop.js_key, prop) for prop in
        [obj for name, obj in inspect.getmembers(sys.modules[profile_properties.__name__])
         if inspect.isclass(obj) and
         issubclass(obj, profile_properties.UsableProperty) and
         obj.__name__ != 'UsableProperty']
    }
    cls.property_by_prefix = {p[1].prefix: (k, p[1]) for k, p in cls.data_types.items()}

    for data_type in cls.data_types:
        setattr(cls, data_type, property(functools.partial(cls.get_property_dict, data_type=data_type)))
    return cls


@set_data_type_properties
class Profile(object):

    db_lookup_fail_check_ttl = 24 * 60 * 60
    domain = DEFAULT_DOMAIN
    fast_clean_threshold = DEFAULT_FAST_CLEAN_THRESHOLD
    redis_client = DEFAULT_REDIS_CLIENT
    django_profile_model = DEFAULT_DJANGO_PROFILE_MODEL
    django_pointer_model = DEFAULT_DJANGO_POINTER_MODEL
    django_connection_tuple = DEFAULT_DJANGO_CONNECTION_TUPLE
    django_count_func = DEFAULT_DJANGO_COUNT_FUNC
    profile_ttl = DEFAULT_PROFILE_TTL
    profile_ttl_margin = DEFAULT_PROFILE_TTL_MARGIN
    user_ttl = DEFAULT_USER_TTL
    user_data_ttl_margin = DEFAULT_USER_DATA_TTL_MARGIN
    clean_queue_ttl = DEFAULT_CLEAN_QUEUE_TTL

    def __init__(self,
                 key=None,
                 user_id=None,
                 profile_id=None,
                 session_id=None,
                 time=None,
                 raw_input=None,
                 updated=None,
                 created=None,
                 props_updated=None,
                 props_created=None,
                 init=True):

        now = pytz.utc.localize(datetime.datetime.utcnow())

        self.raw_input = raw_input
        self.user_id = user_id
        self.key = key
        self.session_id = session_id
        self.updated = updated or time or now
        self.created = created or time or now
        self.time = time or now
        self.profile_id = profile_id

        if self.domain is None:
            raise ValueError('domain should not be None')

        if self.redis_client is None:
            raise ValueError('redis_client should not be None')

        if init:
            self.build_properties(updated=props_updated,
                                  created=props_created)

    @classmethod
    def usable_django_model(cls):
        if cls.django_profile_model:
            if all(cls.django_connection_tuple):
                if cls.django_connection_tuple[0].connection and not cls.django_connection_tuple[0].is_usable():
                    del cls.django_connection_tuple[1]._connections.default
                return cls.django_profile_model
            else:
                return cls.django_profile_model

    def build_properties(self,
                         updated=None,
                         created=None):

        self.properties = {}

        for key, (data_key, data_type) in self.data_types.items():
            self.properties[key] = self.build_properties_for_type(data_key,
                                                                  data_type,
                                                                  updated=updated,
                                                                  created=created)

    def build_properties_for_type(self,
                                  data_key,
                                  data_type,
                                  updated=None,
                                  created=None):

        data = self.raw_input.get(data_key)

        if not data or len(data) == 0:
            return {}

        return {
            obj['name']: data_type(name=obj['name'],
                                   value=obj.get('value'),
                                   ttl=obj.get('ttl'),
                                   updated=updated,
                                   created=created)
            for obj in data
        }

    def __add__(self, other):

        if isinstance(other, int) and other == 0:
            return self

        assert self.__class__ == other.__class__, 'Cannot add {} to {}'\
            .format(self.__class__.__name__, other.__class__.__name__)

        assert self.domain == other.domain, 'Cannot add profiles for different domains'
        assert self.redis_id == other.redis_id, 'Cannot add profiles for different Redis instances'

        props1 = self.properties.copy()
        props2 = other.properties.copy()
        props3 = {}

        data_types = set(props1.keys()).union(set(props2.keys()))

        for data_type in data_types:
            p1 = props1.get(data_type, {})
            p2 = props2.get(data_type, {})
            p3 = {}
            names = set(p1.keys()).union(set(p2.keys()))
            for name in names:
                p3[name] = p1.get(name, 0) + p2.get(name, 0)
            props3[data_type] = p3

        updated = max(self.updated, other.updated)
        created = min(self.created, other.created)

        profile = self.__class__(user_id=self.user_id,
                                 raw_input=None,
                                 updated=updated,
                                 created=created,
                                 init=False)

        profile.properties = props3

        return profile

    def __radd__(self, other):

        return self.__add__(other)

    @classmethod
    def get(cls,
            user_id,
            time,
            force_db_lookup=False,
            fallback_to_db_lookup=False):

        # fallback_to_db_lookup: set to True to fallback to db IF no user profile is found at all in Redis
        # force_db_lookup: set to True do do a db search, no matter what.

        data = cls.redis_client.get_user_profile(
            keys=[
                cls._profile_pool_key(user_id)
            ],
            args=[
                time.timestamp()
            ]
        )
        # dictionary with keys: profile_id and values profile
        data_dict = dict(zip(data[::2], data[1::2]))
        ghost_keys = [key for key, data in data_dict.items() if not data]

        db_fallback = ((len(data_dict) == 0 and fallback_to_db_lookup) or len(ghost_keys) > 0) and \
                      not cls.db_lookup_failed_before(user_id=user_id)

        profiles_from_db = {}

        if force_db_lookup or db_fallback:

            profiles_from_db = cls.from_database_by_user_id(user_id)

            pipe = cls.redis_client.pipeline()
            for p in profiles_from_db.values():
                p.to_cache(key=p.profile_key, add_to_pool=True, pipe=pipe)

            pipe.delete(cls._new_user_detected_key(user_id=user_id))
            pipe.execute()

            data_dict = {k: v for k, v in data_dict.items()
                         if not cls.profile_id_from_key(k.decode()) in profiles_from_db}

        if db_fallback and len(profiles_from_db) == 0:
            cls.set_db_lookup_fail(user_id=user_id)

        profiles = [profile for profile in
                    [cls.from_redis_data(data=d,
                                         key=key,
                                         user_id=user_id,
                                         try_db=False) for key, d in data_dict.items()
                     if not d is None]
                    if not profile is None]

        profiles += list(profiles_from_db.values())

        if len(profiles) == 0:
            return None
        if len(profiles_from_db) >= cls.fast_clean_threshold:
            cls.user_in_cleaning_queue(user_id)

        return sum(profiles)

    @classmethod
    def from_database_by_user_id(cls,
                                 user_id):

        profile_models = cls.usable_django_model().objects.filter(user_id=user_id)
        data = {profile_model.profile_id: cls.from_flat_data(data=json.loads(profile_model.data),
                                                             user_id=user_id)
                for profile_model in profile_models}
        for profile_id, profile in data.items():
            profile.profile_id = profile_id
        return data

    @classmethod
    def db_lookup_failed_before(cls, user_id):

        return cls.redis_client.get(cls._user_not_found_in_db_key(user_id=user_id)) == b'1'

    @classmethod
    def set_db_lookup_fail(cls, user_id):

        cls.redis_client.set(cls._user_not_found_in_db_key(user_id=user_id), value='1',
                                        nx=True, ex=cls.db_lookup_fail_check_ttl)

    def store_in_db(self, data=None):

        max_tries = 3

        if self.key is None:
            self.key = self.new_profile_key

        if data is None:
            datastring = json.dumps(self.flat_data)
        else:
            datastring = json.dumps(data)

        for i in range(max_tries):
            try:
                self.usable_django_model().objects.update_or_create(
                    profile_id=self.profile_id_from_key(self.key),
                    user_id=self.user_id,
                    defaults={'data': datastring})
                return
            except Exception as e:
                if 'OperationalError' in e.__class__.__name__:
                    error = e
                    time.sleep(1 + random.random() / 10)
            raise error

    def delete_in_db(self):

        try:
            self.usable_django_model().objects.get(profile_id=self.profile_id).delete()
        except self.django_profile_model.DoesNotExist:
            pass

    def delete_in_cache(self):

        self.redis_client.delete_in_cache(
            keys=[
                self.key,
                self.all_profile_keys_key],
            args=[])

    @classmethod
    def switch_profiles(cls,
                        user_id,
                        new_profile_key,
                        old_profile_keys):

        return cls.redis_client.switch_profiles(
            keys=[
                cls._profile_pool_key(user_id=user_id),
                cls._all_profile_keys_key()
            ],
            args=[
                json.dumps(old_profile_keys),
                new_profile_key
            ]
        )

    def store_user_pointers(self):

        pointers = self.redis_client.get_all_user_pointers_if_main_profile(
            keys=[self.all_pointers_key],
            args=[self.user_id])

        pointers = [p.decode() if isinstance(p, bytes) else p for p in pointers]
        pointers = [p[len(self.pointer_prefix()):] for p in pointers]

        max_tries = 3
        error = None
        errors = []
        for pointer in pointers:
            for i in range(max_tries):
                try:
                    self.django_pointer_model.objects.update_or_create(
                        pointer=pointer,
                        defaults={'user_id': self.user_id}
                    )
                    error = None
                    break
                except Exception as e:
                    if 'OperationalError' in e.__class__.__name__:
                        error = e
                        time.sleep(1.0 + random.random() / 10)
                    else:
                        raise e
            if not error is None:
                errors.append(error)

        if len(errors) > 0:
            raise errors[0]

        return len(pointers)

    def reset_user_not_found(self):

        self.redis_client.delete(self.user_not_found_in_db_key)

    def remove_from_to_be_cleaned_queue(self):

        self.redis_client.srem(self.users_to_be_cleaned_key, self.user_id)

    @classmethod
    def get_stitched(cls,
                     user_ids,
                     time,
                     fallback_to_db_lookup=False):

        profile_pool_keys = [cls._profile_pool_key(user_id) for user_id in user_ids]
        data = cls.redis_client.get_stitched_user_profile(keys=[], args=[json.dumps(profile_pool_keys), time.timestamp()])
        # a dictionary with profile_pool_key as key and corresponding (profile_key - profile) dict as value
        data_dict = {k.decode(): {pk.decode(): pr for pk, pr in dict(zip(v[::2], v[1::2])).items()} if v else None
                     for k, v in dict(zip(data[::2], data[1::2])).items()}
        incomplete_users = {cls._user_id_from_profile_pool_key(k): v for k, v in data_dict.items() if not v or any(not bool(x) for x in v.values())}
        complete_users = {u:p for u,p in {cls._user_id_from_profile_pool_key(k): v for k, v in data_dict.items()}.items() if not u in incomplete_users}

        complete_profiles = [p for p in [cls.from_redis_data(data=d,
                                                             key=key,
                                                             user_id=user_id) for user_id, user_data in complete_users.items() for key, d in user_data.items()] if not p is None]

        missing_users = []

        if fallback_to_db_lookup:

            from_db = cls.from_database_by_user_ids(incomplete_users.keys())
            complemented_profiles = []
            for user_id, profiles_for_user in incomplete_users.items():
                from_db_for_user = from_db.get(user_id, [])
                if len(profiles_for_user) == 0:
                    if len(from_db_for_user) ==0:
                        missing_users.append(user_id)
                    else:
                        complemented_profiles.extend([cls.from_redis_data(profile.data,
                                                                          key=profile.key,
                                                                          user_id=user_id) for profile in from_db_for_user])
                else:
                    for profile in from_db_for_user:
                        if not profile.key in profiles_for_user:
                            profiles_for_user[profile.key] = profile.data
                complemented_profiles.extend(cls.from_redis_data(data=d,
                                                                 key=key,
                                                                 user_id=user_id) for key,d in profiles_for_user.items())
        else:
            complemented_profiles = [cls.from_redis_data(data=d,
                                                         key=key,
                                                         user_id=user_id) for user_id, user_data in incomplete_users.items() for key, d in user_data.items()]

        complemented_profiles = [p for p in complemented_profiles if not p is None]

        final_profiles = complete_profiles + complemented_profiles

        if len(final_profiles) == 0:
            return missing_users, None

        profile = sum(final_profiles)

        return missing_users, profile

        # if fallback is true, retrieve from database for those users (if users are missing in db, something is wrong,
        # however we should still delete them from stitch pool)

    def to_cache(self, key, add_to_pool=False, pipe=None):

        if pipe:
            pipe.hmset(key, self.flat_data)
            pipe.expire(key, self.profile_ttl + self.profile_ttl_margin)
            if add_to_pool:
                pipe.sadd(self.profile_pool_key, key)
                pipe.expire(self.profile_pool_key, self.user_ttl + self.user_data_ttl_margin)
        else:
            self.redis_client.hmset(key, self.flat_data)
            self.redis_client.expire(key, self.profile_ttl + self.profile_ttl_margin)
            if add_to_pool:
                self.redis_client.sadd(self.profile_pool_key, key)
                self.redis_client.expire(self.profile_pool_key, self.user_ttl + self.user_data_ttl_margin)

    def init_profile_to_cache(self,
                              time):

        created = self.redis_client.set_profile_if_new_user(
            keys=[
                self.user_hash_key,
                self.all_profile_keys_key,
                self.new_profile_key,
                self.profile_pool_key,
                self.new_user_detected_key
            ],
            args=[
                json.dumps([y for x in self.flat_data.items() for y in x]),
                time.timestamp()
            ]
        )
        if created is None:
            return False
        return bool(int(created.decode()))

    @classmethod
    def from_database_by_user_ids(cls,
                                  user_ids):

        user_ids = [u for u in user_ids if not cls.db_lookup_failed_before(u)]
        profile_models = cls.usable_django_model().objects.filter(user_id__in=user_ids)

        result = {}

        for profile_model in profile_models:
            user_id = str(profile_model.user_id)
            profile = cls.from_flat_data(data=json.loads(profile_model.data),
                                         user_id=user_id)
            profile.profile_id = profile_model.profile_id
            result[user_id] = result.get(user_id, []) + [profile]

        failed_users = [u for u in user_ids if not u in result]
        for failed_user_id in failed_users:
            cls.set_db_lookup_fail(failed_user_id)

        return result

    @classmethod
    def from_database(cls,
                      key,
                      user_id):
        try:
            profile_model = cls.usable_django_model().objects.get(profile_id=cls.profile_id_from_key(key),
                                                             user_id=user_id)
        except cls.django_profile_model.DoesNotExist:
            return None
        return cls.from_flat_data(data=json.loads(profile_model.data),
                                  user_id=user_id)

    @classmethod
    def from_flat_data(cls,
                       data,
                       user_id):

        names = {'_'.join(n.split('_')[:-1]) for n in data if not n in ('_updated', '_created', '_user_hash')}

        properties = {}

        for data_type_name in names:

            _t = data_type_name.split('_')
            prefix, name = _t[0] + '_', '_'.join(_t[1:])
            if not prefix in cls.property_by_prefix:
                continue
            data_type, profile_property = cls.property_by_prefix[prefix]
            props = properties.get(data_type, {})
            value = data[data_type_name + profile_properties.PROFILE_VALUE_POSTFIX]
            updated = cls.timestamp_to_datetime(data.get(
                data_type_name + profile_properties.PROFILE_VALUE_UPDATED_POSTFIX))
            created = cls.timestamp_to_datetime(data.get(
                data_type_name + profile_properties.PROFILE_VALUE_CREATED_POSTFIX))
            expire_at = cls.timestamp_to_datetime(
                data.get(data_type_name + profile_properties.PROFILE_VALUE_EXPIRE_AT_POSTFIX))
            props[name] = profile_property.from_redis_data(name=name,
                                                           value=value,
                                                           updated=updated,
                                                           created=created,
                                                           expire_at=expire_at)
            properties[data_type] = props

        _updated = cls.timestamp_to_datetime(data['_updated'])
        _created = cls.timestamp_to_datetime(data['_created'])

        profile = cls(user_id=user_id,
                      updated=_updated,
                      created=_created,
                      init=False)

        profile.properties = properties

        return profile

    @classmethod
    def get_to_be_cleaned_users(cls,
                                number=1000):
        user_ids = cls.redis_client.srandmember(cls._users_to_be_cleaned_key(), number=number)
        return [user_id.decode() if isinstance(user_id, bytes) else user_id for user_id in user_ids]

    @classmethod
    def get_expired(cls,
                    num=300,
                    start=0,
                    dev=False):

        now = pytz.utc.localize(datetime.datetime.utcnow()).timestamp()
        expired_profiles = cls.redis_client.zrangebyscore(cls._all_profile_keys_key(),
                                                          min='-inf',
                                                          max='+inf' if dev else (now - cls.profile_ttl),
                                                          start=start,
                                                          num=num,
                                                          withscores=True)
        return [cls(key=profile_key.decode(),
                    time=pytz.utc.localize(datetime.datetime.utcfromtimestamp(timestamp)),
                    init=False) for profile_key, timestamp in expired_profiles]

    def lock(self, ttl):
        return Lock(self.profile_id_from_key(self.key), self.redis_client, ttl=ttl * 1000)

    def load_and_finalize(self):

        data = self.redis_client.finalize_profile(keys=[self.key], args=[])

        if data is None:
            raise exceptions.ProfileNotFoundError

        user_hash_key, currently_active, profile_data = data
        self.user_id = self.user_id_from_user_hash_key(user_hash_key.decode())
        self.currently_active = currently_active == b'1'
        profile_data = dict(zip(profile_data[::2], profile_data[1::2]))
        self.profile_data = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in profile_data.items()}

    def completely_remove_from_cache(self):

        self.redis_client.completely_remove_from_cache(
            keys=[
                self.profile_key,
                self.profile_pool_key,
                self.all_profile_keys_key
            ],
            args=[])

    def update(self,
               pointers=None,
               stitch_keys=None):

        new_user_detected = self.redis_client.update_profile(
            keys=[
                self.user_hash_key,
                self.all_profile_keys_key,
                self.all_pointers_key,
                self.new_profile_key,
                self.profile_pool_key,
                self.new_user_detected_key,
                self.stitch_pool_key],
            args=[
                self.lua_update_string,
                self.time.timestamp(),
                str(self.session_id or 'none'),
                str(self.user_id),
                json.dumps(self.create_pointers(pointers)),
                json.dumps(self.create_stitch_keys(stitch_keys))
            ]
        )
        return bool(int(new_user_detected.decode()))

    @classmethod
    def user_in_cleaning_queue(cls, user_id):

        cls.redis_client.sadd(cls._users_to_be_cleaned_key(), str(user_id))
        cls.redis_client.expire(cls._users_to_be_cleaned_key(), cls.clean_queue_ttl)

    @property
    def stitch_pool_key(self):

        return f'st:u:p:{self.domain}:{self.user_id}'

    def create_pointers(self, pointers):

        if pointers is None:
            return []
        return [self.pointer_from_input(p) for p in pointers]

    def create_stitch_keys(self, stitch_keys):

        if stitch_keys is None:
            return []
        return stitch_keys

    @property
    def lua_update_string(self):

        data = {}

        for data_type, properties in self.properties.items():
            redis_keys = [prop.redis_keys for prop in properties.values()]
            if redis_keys:
                data.update({data_type: redis_keys})
        return json.dumps(data)

    @staticmethod
    def get_property_dict(instance, data_type):

        return instance.properties.get(data_type, {})

    @staticmethod
    def to_short_data(props):

        return {k: v.output_value for k, v in props.items()}

    @property
    def data(self):

        data = {
            'start': self.created.isoformat(),
            'startTimestampMillis': self.created.timestamp() * 1000,
            'updated': self.updated.isoformat(),
            'updatedTimestampMillis': self.updated.timestamp() * 1000,
            **{v[0]: self.to_short_data(getattr(self, k)) for k, v in self.data_types.items()}
        }
        return {k: v for k, v in data.items() if isinstance(v, float) or len(v) > 0}

    @classmethod
    def timestamp_to_datetime(cls, value):

        if value is None:
            return None
        return pytz.utc.localize(datetime.datetime.utcfromtimestamp(float(value)))

    @classmethod
    def get_user_ids_with_multiple_profiles(cls,
                                            num,
                                            start):

        result = cls.usable_django_model().objects.all().values('user_id').annotate(
            count=cls.django_count_func('user_id')).filter(count__gt=1).order_by()[start:start + num]
        return [str(res['user_id']) for res in result]

    @classmethod
    def multiple_from_database(cls,
                               keys,
                               user_id):

        keys = [key.decode() if isinstance(key, bytes) else key for key in keys]
        profile_ids = [cls.profile_id_from_key(key) for key in keys]

        profile_models = list(cls.usable_django_model().objects.filter(profile_id__in=profile_ids, user_id=user_id))
        profiles = {cls._profile_key(profile_model.profile_id):
                        cls.from_flat_data(data=json.loads(profile_model.data),
                                           user_id=user_id)
                    for profile_model in profile_models}

        for profile_key, profile in profiles.items():
            profile.to_cache(key=profile_key)
        missing = list(set(profile_ids) - set(str(profile_model.profile_id) for profile_model in profile_models))
        for profile_id in missing:
            p = cls(user_id=user_id,
                    profile_id=profile_id,
                    init=False)
            p.completely_remove_from_cache()
        return profiles

    @classmethod
    def from_redis_data(cls,
                        data,
                        key,
                        user_id,
                        try_db=True):

        key = key.decode() if isinstance(key, bytes) else key
        if not data:
            if try_db:
                profile = cls.from_database(key,
                                            user_id=user_id)
                if not profile is None:
                    profile.to_cache(key)
                return profile
            return None
        else:
            data = [x.decode() if isinstance(x, bytes) else x for x in data]
            data = dict(zip(data[::2], data[1::2]))
            return cls.from_flat_data(data=data,
                                      user_id=user_id)

    @property
    def flat_data(self):

        data = {'_updated': self.updated.timestamp(),
                '_created': self.created.timestamp(),
                '_user_hash': self.user_hash_key}

        for data_type, properties in self.properties.items():
            for prop in properties.values():
                data.update(prop.flat_redis_keys)
        return data

    @property
    def user_hash_key(self):
        return self._user_hash_key(user_id=self.user_id)

    @classmethod
    def _user_hash_key(cls, user_id):
        return f'u:h:{cls.domain}:{user_id}'

    @classmethod
    def user_id_from_user_hash_key(cls, user_hash_key):
        return user_hash_key.split(':')[-1]

    @staticmethod
    def profile_id_from_key(key):

        return key.split(':')[-1]

    @property
    def all_profile_keys_key(self):

        return self._all_profile_keys_key()

    @classmethod
    def _all_profile_keys_key(cls):

        return f'u:pk:{cls.domain}:all'

    @property
    def profile_pool_key(self):

        return self._profile_pool_key(user_id=self.user_id)

    @classmethod
    def _profile_pool_key(cls, user_id):

        return f'u:pp:{cls.domain}:{user_id}'

    @classmethod
    def _user_id_from_profile_pool_key(cls, profile_pool_key):

        return profile_pool_key.split(':')[-1]

    @property
    def new_user_detected_key(self):

        return self._new_user_detected_key(user_id=self.user_id)

    @classmethod
    def _new_user_detected_key(cls, user_id):

        return f'u:nd:{cls.domain}:{user_id}'

    @property
    def user_not_found_in_db_key(self):
        return self._user_not_found_in_db_key(user_id=self.user_id)

    @classmethod
    def _user_not_found_in_db_key(cls, user_id):
        return f'u:nf:{cls.domain}:{user_id}'

    @property
    def new_profile_key(self):

        self.profile_id = str(uuid.uuid4())
        return self.profile_key

    @property
    def users_to_be_cleaned_key(self):
        return self._users_to_be_cleaned_key()

    @classmethod
    def _users_to_be_cleaned_key(cls):
        return f'u:tbc:{cls.domain}'

    @property
    def profile_key(self):
        return self._profile_key(profile_id=self.profile_id)

    @classmethod
    def _profile_key(cls, profile_id):
        return f'u:p:{cls.domain}:{profile_id}'

    @property
    def all_pointers_key(self):
        return self._all_pointers_key(user_id=self.user_id)

    @classmethod
    def _all_pointers_key(cls, user_id):
        return f'u:pt:{cls.domain}:{user_id}'

    @staticmethod
    def pointer_from_input(value):
        return f'{Profile.pointer_prefix()}{value}'

    @staticmethod
    def pointer_prefix():
        return 'u:pt:'

    @property
    def redis_id(self):
        if not hasattr(self, '_redis_id') or self._redis_id is None:
            conn_kwargs = self.redis_client.get_connection_kwargs()
            self._redis_id = f'{conn_kwargs["host"]}:{conn_kwargs["port"]}:{conn_kwargs["db"]}'
        return self._redis_id