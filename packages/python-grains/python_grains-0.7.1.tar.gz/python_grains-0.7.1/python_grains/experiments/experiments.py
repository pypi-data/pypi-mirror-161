import hashlib

DEFAULT_N_CHARS = 10  # should not exceed 32 (half the length of the hex representation of a sha256 hash)
DEFAULT_EXPERIMENTS_RANGE_SEED = 'wjBr2FiEdFUKMz523E7Ro3kuSc5v5Oxh'

def experiment_init(self):
    self.variants = [v() for v in self.variants]
    self.initialize()

def variant_init(self):
    self.initialize()

class Variant(object):

    def __init__(self):
        raise NotImplementedError('Class should be setup by using Variant.setup')

    def initialize(self):
        pass

    @classmethod
    def setup(cls, **kwargs):

        mandatory_kwargs = {
            'id',
            'name',
            'prop' }

        defaults = {
            'n_chars': DEFAULT_N_CHARS }

        missing = mandatory_kwargs - set(kwargs.keys())
        if len(missing) > 0:
            raise Exception(f'Missing configurations: {", ".join(missing)}')

        for prop, value in defaults.items():
            if not prop in kwargs:
                kwargs[prop] = value

        if not '__init__' in kwargs:
            kwargs['__init__'] = variant_init

        return type(cls.__name__ + '_' + kwargs['id'], (cls,), kwargs)

    def user_in_variant(self,
                        user_id):

        p = int(hashlib.sha256((str(user_id) + self.seed).encode('utf-8')).hexdigest()[:self.n_chars], 16) / 16 ** self.n_chars
        return p <= self.cum_prob

    @property
    def data(self):

        return {
            'id': self.id,
            'name': self.name
        }

class Experiment(object):

    def __init__(self):
        raise NotImplementedError('Class should be setup by using Experiment.setup')

    def __repr__(self):
        return str('<Experiment: ' + self.name + '>')

    def initialize(self):
        pass

    @classmethod
    def setup(cls, **kwargs):

        mandatory_kwargs = {
            'id',
            'name',
            'seed'}

        defaults = {
            'use_range': False,
            'range_start': None,
            'range_end': None,
            'hostnames': None,
            'origin_type': 'all',
            'n_chars': DEFAULT_N_CHARS,
            'variants': []
        }

        missing = mandatory_kwargs - set(kwargs.keys())
        if len(missing) > 0:
            raise Exception(f'Missing configurations: {", ".join(missing)}')

        if 'use_range' in kwargs and kwargs['use_range'] and not 'range_seed' in kwargs:
            raise Exception(f'Must provide range_seed if "use_range==True"')

        if 'variants' in kwargs:
            sort_key = kwargs.get('variant_sort_key') or 'id'
            kwargs['variants'] = cls.prepare_variants(kwargs['variants'], seed=kwargs['seed'], sort_key=sort_key)

        for prop, value in defaults.items():
            if not prop in kwargs:
                kwargs[prop] = value

        kwargs['__init__'] = experiment_init

        return type(cls.__name__ + '_' + kwargs['id'], (cls,), kwargs)

    def set_variants(self,
                     variants,
                     sort_key='id'):

        self.variants = self.prepare_variants(variants, self.seed, sort_key=sort_key)

    @staticmethod
    def prepare_variants(variants, seed, sort_key='id'):

        assert all(isinstance(var, Variant) or issubclass(var, Variant) for var in variants)

        variants = sorted(variants, key=lambda v: getattr(v, sort_key))
        for variant in variants:
            variant.seed = seed

        total_prop = sum(v.prop for v in variants)
        cum_prob = 0
        for variant in variants:
            cum_prob += variant.prop / total_prop
            variant.cum_prob = cum_prob

        return variants

    def origin_type_allowed(self,
                            origin_type):

        return self.origin_type == 'all' or origin_type.lower() == self.origin_type

    def hostname_match(self,
                       hostname,
                       match_string):

        if match_string.startswith('.'):
            return hostname.lower().endswith(match_string[1:])
        else:
            return hostname.lower() == match_string

    def hostname_allowed(self,
                         hostname):

        if not self.hostnames:
            return True
        return any(self.hostname_match(hostname, m) for m in self.hostnames)

    def user_in_experiment(self,
                           user_id,
                           origin_type,
                           hostname):

        if not self.origin_type_allowed(origin_type=origin_type):
            return False
        if not self.hostname_allowed(hostname=hostname):
            return False

        if self.use_range:
            p = int(
                hashlib.sha256((str(user_id) + self.range_seed).encode('utf-8')).hexdigest()[-self.n_chars:],
                16) / 16 ** self.n_chars
            if not self.range_start < p <= self.range_end:
                return False

        return True

    def get_variant_for_user(self,
                             user_id):

        for variant in self.variants[:-1]:
            if variant.user_in_variant(user_id):
                return variant
        return self.variants[-1]

    def data_for_user(self,
                      user_id,
                      verbose=False):
        variant = self.get_variant_for_user(user_id=user_id)
        variant_data = variant.data
        variant_id = variant_data['id']

        if verbose:

            return {
                'id': self.id,
                'name': self.name,
                'expVarId': self.id + ':' + variant_id,
                'variant': variant.data}

        return {
            'id': self.id,
            'expVarId': self.id + ':' + variant_id,
            'variant': {'id': variant.data['id']}}