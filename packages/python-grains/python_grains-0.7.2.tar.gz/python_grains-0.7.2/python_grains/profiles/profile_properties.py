import datetime
import pytz
import json

PROFILE_VALUE_POSTFIX = '_v'
PROFILE_VALUE_UPDATED_POSTFIX = '_u'
PROFILE_VALUE_CREATED_POSTFIX = '_c'
PROFILE_VALUE_EXPIRE_AT_POSTFIX = '_e'

class ProfilePropertyError(Exception): pass


class ProfileProperty(object):

    type = None
    prefix = None

    def __init__(self,
                 name,
                 value=None,
                 updated=None,
                 created=None,
                 ttl=None,
                 expire_at=None):

        self.name = name
        self.value = self.validate(value) if not value is None else value

        now = pytz.utc.localize(datetime.datetime.utcnow())
        self.updated = updated or now
        self.created = created or now

        if ttl:
            self.expire_at = now + datetime.timedelta(seconds=ttl)
        else:
            self.expire_at = expire_at or None

    def __repr__(self):

        return str(self.__class__.__name__) + '(`{}`:{})'.format(self.name, self.value)

    def validate(self,
                 value):

        if self.type:
            try:
                value = self.type(value)
            except (ValueError, TypeError):
                raise ProfilePropertyError(f'Value must be of type (or coercible to): {self.type.__name__}')

        return value

    def __add__(self,
                other):

        if isinstance(other, int) and other == 0:
            return self

        assert self.__class__ == other.__class__, 'Cannot add {} to {}'.format(self.__class__.__name__,
                                                                               other.__class__.__name__)
        assert self.name == other.name, 'Can only add properties with the same name.'
        assert isinstance(self.value, type(other.value)), 'Cannot add {} to {}'.format(type(self.value), type(other.value))

        return self.combine(other)

    def __radd__(self,
                 other):

        return self.__add__(other)

    def combine(self,
                other):

        new_value = self.value + other.value
        new_updated = max([self.updated, other.updated])
        new_created = min([self.created, other.created])
        new_expire_at = self.combine_expire(other)

        return self.__class__(self.name, new_value, updated=new_updated, created=new_created, expire_at=new_expire_at)

    def combine_expire(self,
                       other):

        if self.expire_at is None and other.expire_at is None:
            return None
        if self.expire_at is None:
            return other.expire_at
        if other.expire_at is None:
            return self.expire_at
        if self.updated > other.updated:
            return self.expire_at
        if self.updated < other.updated:
            return other.updated
        return max([self.expire_at, other.expire_at])

    def copy_off(self, obj, expire_at):

        return self.__class__(obj.name, obj.value, updated=obj.updated, created=obj.created, expire_at=expire_at)

    @classmethod
    def from_redis_data(cls,
                        name,
                        value=None,
                        updated=None,
                        created=None,
                        ttl=None,
                        expire_at=None):

        return cls(name=name,
                   value=cls.value_from_redis(value),
                   updated=updated,
                   created=created,
                   ttl=ttl,
                   expire_at=expire_at)

    @classmethod
    def value_from_redis(cls, value):
        return value

    @classmethod
    def value_to_redis(cls, value):

        return value

    @property
    def expired(self):

        if self.expire_at:
            return self.expire_at < pytz.utc.localize(datetime.datetime.utcnow())
        return False

    @property
    def output_value(self):
        return self.value

    @property
    def redis_keys(self):

        s = self.prefix + self.name
        d = {'key': s}
        if not self.value is None:
            d.update({'value': self.value_to_redis(self.value)})
        if self.expire_at:
            d.update({'expire_at': self.expire_at.timestamp()})
        if self.extra_redis_args:
            d.update(self.extra_redis_args)
        return d

    @property
    def extra_redis_args(self):
        return {}

    @property
    def flat_redis_keys(self):

        s = self.prefix + self.name
        d = {
            s + PROFILE_VALUE_POSTFIX: self.value_to_redis(self.value),
            s + PROFILE_VALUE_UPDATED_POSTFIX: self.updated.timestamp(),
            s + PROFILE_VALUE_CREATED_POSTFIX: self.created.timestamp()
        }
        if self.expire_at:
            d.update({s + PROFILE_VALUE_EXPIRE_AT_POSTFIX: self.expire_at.timestamp()})
        return d

    @property
    def short_repr(self):

        return {self.name: self.output_value}

    @property
    def dict_repr(self):

        d = {
            'name': self.name,
            'value': self.output_value,
            'updated': self.updated.isoformat(),
            'created': self.created.isoformat()
        }

        if self.expire_at:
            d['expire_at'] = self.expire_at.isoformat()

        return d

class ProfileString(ProfileProperty):

    type = str


class ProfileFloat(ProfileProperty):

    type = float


class ProfileBoolean(ProfileProperty):

    type = bool

    @classmethod
    def value_from_redis(cls, value):

        return value in ('1', b'1', 'True', b'True', 'true', b'true', True, 1)

    @classmethod
    def value_to_redis(cls, value):

        return int(value)


class OR(object):

    def combine(self, other):
        new_value = self.value or other.value
        new_updated = max([self.updated, other.updated])
        new_created = min([self.created, other.created])
        new_expire_at = self.combine_expire(other)

        return self.__class__(self.name, new_value, updated=new_updated, created=new_created, expire_at=new_expire_at)


class AND(object):

    def combine(self, other):
        new_value = self.value and other.value
        new_updated = max([self.updated, other.updated])
        new_created = min([self.created, other.created])
        new_expire_at = self.combine_expire(other)

        return self.__class__(self.name, new_value, updated=new_updated, created=new_created, expire_at=new_expire_at)


class LastUpdated(object):

    def combine(self, other):
        expire_at = self.combine_expire(other)

        if self.updated < other.updated:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class LastCreated(object):

    def combine(self, other):
        expire_at = self.combine_expire(other)

        if self.created < other.created:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class FirstUpdated(object):

    def combine(self, other):
        expire_at = self.combine_expire(other)

        if self.updated > other.updated:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class FirstCreated(object):

    def combine(self, other):
        expire_at = self.combine_expire(other)

        if self.created > other.created:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class SmallestValue(object):

    def combine(self, other):
        expire_at = self.combine_expire(other)

        if self.value > other.value:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class LargestValue(object):

    def combine(self, other):

        expire_at = self.combine_expire(other)

        if self.value < other.value:
            return self.copy_off(other, expire_at=expire_at)
        return self.copy_off(self, expire_at=expire_at)


class CounterWithTimeWindow(ProfileProperty):

    window_step_size = datetime.timedelta(days=1)
    count_from = datetime.datetime(2021, 1, 1, 0, 0, 0)
    timezone = pytz.timezone('Europe/Amsterdam')

    @classmethod
    def threshold_date(cls):

        return pytz.utc.localize(datetime.datetime.now()).astimezone(cls.timezone) \
               - cls.window_size * cls.window_step_size

    @classmethod
    def threshold_day_counter(cls):

        return (cls.threshold_date().date() - cls.count_from.date()).days

    @classmethod
    def current_day_counter(cls):

        return (pytz.utc.localize(datetime.datetime.now()).astimezone(cls.timezone).date() - cls.count_from.date()).days

    @classmethod
    def _current_value(cls, value):

        return {ts: v for ts,v in value.items() if int(ts) > cls.threshold_day_counter()}

    @property
    def current_value(self):

        return self._current_value(value=self.value)

    @classmethod
    def value_from_redis(cls, value):
        value = value.decode() if isinstance(value, bytes) else value
        data = {int(ts): int(val) for ts, val in json.loads(value).items()}
        return cls._current_value(data)

    @classmethod
    def value_to_redis(cls, value):

        return json.dumps(cls._current_value(value))

    @property
    def output_value(self):

        return sum(self.current_value.values())

    def combine(self, other):

        new_updated = max([self.updated, other.updated])
        new_created = min([self.created, other.created])
        new_expire_at = self.combine_expire(other)

        new_value = self.current_value
        for ts, val in other.current_value.items():
            new_value[ts] = new_value.get(ts, 0) + val

        return self.__class__(self.name, new_value, updated=new_updated, created=new_created, expire_at=new_expire_at)

    @property
    def extra_redis_args(self):
        return {
            'thr': self.threshold_day_counter()}


class UsableProperty(object): pass

###### Use one of these: #######

class Counter(ProfileProperty, UsableProperty):
    type = int
    prefix = 'ctr_'
    py_key = 'counters'
    js_key = 'counters'

class CounterWithTimeWindow30(CounterWithTimeWindow, UsableProperty):
    type = dict
    prefix = 'tmctr30_'
    py_key = 'time_window30_counters'
    js_key = 'timeWindow30Counters'
    window_size = 30

class SummedFloat(ProfileFloat, UsableProperty):
    prefix = 'sumflt_'
    py_key = 'summed_floats'
    js_key = 'summedFloats'


class LastUpdatedFloat(LastUpdated, ProfileFloat, UsableProperty):
    prefix = 'luflt_'
    py_key = 'last_updated_floats'
    js_key = 'lastUpdatedFloats'


class FirstCreatedFloat(FirstCreated, ProfileFloat, UsableProperty):
    prefix = 'fcflt_'
    py_key = 'first_created_floats'
    js_key = 'firstCreatedFloats'


class SmallestFloat(SmallestValue, ProfileFloat, UsableProperty):
    prefix = 'sflt_'
    py_key = 'smallest_floats'
    js_key = 'smallestFloats'


class LargestFloat(LargestValue, ProfileFloat, UsableProperty):
    prefix = 'lflt_'
    py_key = 'largest_floats'
    js_key = 'largestFloats'


class LastUpdatedString(LastUpdated, ProfileString, UsableProperty):
    prefix = 'lustr_'
    py_key = 'last_updated_strings'
    js_key = 'lastUpdatedStrings'


class FirstCreatedString(FirstCreated, ProfileString, UsableProperty):
    prefix = 'fcstr_'
    py_key = 'first_created_strings'
    js_key = 'firstCreatedStrings'


class OrBoolean(OR, ProfileBoolean, UsableProperty):
    prefix = 'obln_'
    py_key = 'or_booleans'
    js_key = 'orBooleans'


class AndBoolean(AND, ProfileBoolean, UsableProperty):
    prefix = 'abln_'
    py_key = 'and_booleans'
    js_key = 'andBooleans'
