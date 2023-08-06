from python_grains.dynamic_settings.lua import LuaScripts

import requests
from requests.sessions import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import datetime
import pytz
import redis
import os

DEFAULT_DEBUG_VERSION = 'QUICK_PREVIEW'
DEFAULT_MAX_AGE = datetime.timedelta(days=21)

class DynamicSetting(object):

    fallback_version = 'fallback'
    download_in_progress_ttl = 5
    data_margin_seconds = 24 * 60 * 60
    max_file_count = 3

    def __init__(self,
                 slug,
                 url,
                 redis_client,
                 domain,
                 logger,
                 data_dir,
                 fallback_data=None,
                 instance_id=None,
                 max_age=DEFAULT_MAX_AGE,
                 download_subkey=None,
                 version_subkey=None,
                 download_options=None,
                 debug_version=DEFAULT_DEBUG_VERSION,
                 fallback_allowed=False,
                 download_timeout=1.5):

        self.slug = slug
        self.content = None
        self.version = None
        self.download_time = None
        self.load_time = None
        self.source = None
        self.fallback_allowed = fallback_allowed

        self.domain = domain
        self.url = url
        self.download_subkey = download_subkey
        self.version_subkey = version_subkey
        self.download_options = download_options or {}

        self.max_age = max_age
        self.debug_version = debug_version
        self.redis_client = redis_client
        self.logger = logger
        self.instance_id = instance_id
        self.data_dir = data_dir
        self.download_try_time = None

        self.fallback_data = fallback_data or {}
        self.download_timeout = download_timeout
        self.data_ttl = self.max_age.total_seconds() + self.data_margin_seconds

        if self.logger:
            self.logger.setDefaultData(data={'slug': self.slug,
                                             'instance_id': self.instance_id,
                                             'url': self.url})
        self.attach_scripts_to_redis_client()

    @classmethod
    def from_setting_object(cls,
                            obj,
                            redis_client,
                            domain,
                            data_dir,
                            logger=None,
                            instance_id=None):

        return cls(slug=obj['slug'],
                   url=obj['url'],
                   redis_client=redis_client,
                   domain=domain,
                   logger=logger,
                   data_dir=data_dir,
                   fallback_data=obj['fallback_data'],
                   instance_id=instance_id,
                   max_age=obj['max_age'],
                   download_options=obj.get('download_options'),
                   download_subkey=obj.get('subkey'),
                   version_subkey=obj.get('version'),
                   fallback_allowed=obj.get('fallback_allowed', False),
                   download_timeout=obj.get('download_timeout', 1.5))

    def get(self, version=None):

        if self.content is None or self.is_fallback:
            self.load_from_storage(version)

        elif self.loaded_version_is_ok(version) and not self.too_old:
            return self.content

        else:
            self.load_from_storage(version)

        if self.content is None:
            self.load_fallback()

        return self.content

    def load_content(self, data, version, download_time, source):

        if hasattr(self, 'process_' + self.slug) and callable(getattr(self, 'process_' + self.slug)):
            data = getattr(self, 'process_' + self.slug)(data)

        self.content = data
        self.version = version
        self.download_time = download_time
        self.load_time = self.current_time
        self.source = source

    def load_from_storage(self, version):

        self.load_from_cache(version)

        if self.content is None or self.too_old:
            self.download()

    def load_from_cache(self, version):

        try:
            data = self.redis_client.get_latest_data(
                keys=[
                    self.current_version_key
                ],
                args=[
                    self.data_key_prefix,
                    self.data_ttl
                ]
            )
            cache_version, download_time, content = self.parse_cache_data(data=data)
            source = 'cache'
        except (redis.connection.ConnectionError, redis.connection.TimeoutError):
            cache_version, download_time, content = self.load_from_file()
            source = 'disk'

        if not content is None:

            if self.is_larger_than_loaded_version(cache_version):
                self.load_content(data=content,
                                  version=cache_version,
                                  download_time=download_time,
                                  source=source)
            if self.loaded_version_is_ok(version):
                return

        self.download()

    def load_from_file(self):

        self.logger.warning('Loading settings from file')
        latest_files = [fn for fn in [self.parse_filename(filename) for filename in os.listdir(self.data_dir)
                                      if filename.endswith('.json') and filename.startswith(self.slug)
                                      and not filename.endswith('fallback.json')] if not fn is None]
        if not latest_files:
            return None, None, None

        latest_file = sorted(latest_files, key=lambda x: int(x['version']))[-1]
        try:
            with open(latest_file['file_path'], 'r') as f:
                data = json.load(f)
                return self.parse_data(data)
        except json.JSONDecodeError:
            return None, None, None


    def parse_data(self, data):

        version = data['version']
        download_time = pytz.utc.localize(datetime.datetime.utcfromtimestamp(float(data['timestamp'])))
        content = data['content']

        return version, download_time, content

    def parse_cache_data(self, data):

        if data is None:
            return None, None, None

        data = data.decode('utf-8') if isinstance(data, bytes) else data
        data = json.loads(data)

        return self.parse_data(data=data)

    def load_fallback(self):

        self.load_content(data=self.fallback_data,
                          version=self.fallback_version,
                          download_time=None,
                          source='fallback')

    def is_debug_version(self, version):

        return str(version).upper() == self.debug_version

    def loaded_version_is_ok(self, version):

        if self.is_debug_version(version) or version is None:
            return True

        try:
            return int(self.version) >= int(version)
        except ValueError:
            return True

    def is_larger_than_loaded_version(self, version):

        if self.version is None or self.version == self.fallback_version:
            return True
        try:
            return int(version) > int(self.version)
        except ValueError:
            return False

    def attach_scripts_to_redis_client(self):

        self.redis_client.set_data_with_version = self.redis_client.register_script(
            LuaScripts.set_data_with_version())
        self.redis_client.get_latest_data = self.redis_client.register_script(
            LuaScripts.get_latest_data())
        self.redis_client.set_download_in_progress = self.redis_client.register_script(
            LuaScripts.set_download_in_progress())

    def validate_download_data(self, data):

        if hasattr(self, 'validate_' + self.slug) and callable(getattr(self, 'validate_' + self.slug)):
            valid, error_message = getattr(self, 'validate_' + self.slug)(data)
            if not valid:
                self.logger.error(f'Response from url did not validate', data={'error': error_message})
                return
        return data

    def parse_download_data(self, data):

        if not self.version_subkey is None:
            if not isinstance(data, dict) or not self.version_subkey in data:
                self.logger.error(f'Response from url should be a JSON object containing the key {self.version_subkey}')
                return None, None
            version = str(data[self.version_subkey])
        else:
            # round this bigtime, otherwise multiple instances will cascade download files
            version = str(self.current_timestamp // 1814400 * 1814400)

        if not self.download_subkey is None:
            if not isinstance(data, dict) or not self.download_subkey in data:
                self.logger.error(f'Response from url should be a JSON object containing the key {self.download_subkey}')
                return None, None
            data = data[self.download_subkey]

        return version, data

    def download_in_progress(self):

        if not self.download_try_time is None and \
                self.download_try_time > self.current_time - datetime.timedelta(seconds=self.download_in_progress_ttl):
            return True
        self.download_try_time = self.current_time

        try:
            if self.redis_client.set_download_in_progress(
                    keys=[self.download_in_progress_key],
                    args=[self.download_in_progress_ttl]
            ) is None:
                return True
        except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
            return False

    def download(self):

        try:
            r = self.session.get(url=self.url, **self.download_options, timeout=self.download_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error('Failed to get data from url', data={'error': str(e)})
            return

        try:
            data = r.json()
        except json.JSONDecodeError:
            self.logger('Response from url was no valid json')
            return

        version, data = self.parse_download_data(data=data)
        if data is None:
            return

        data = self.validate_download_data(data=data)
        if data is None:
            return

        download_time = self.current_time
        self.load_content(data=data,
                          version=version,
                          download_time=download_time,
                          source='download')

        try:
            self.write_data_to_redis(data=data, version=version, download_time=download_time)
        except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
            pass
        self.write_data_to_file(data=data, version=version, download_time=download_time)


    def write_data_to_file(self, data, version, download_time):

        data = self.build_data_object(content=data, version=version, download_time=download_time)
        file_path = self.build_file_path(version=version)
        with open(file_path, 'w') as f:
            json.dump(data, f)
        self.constrain_file_count()

    def constrain_file_count(self):

        latest_files = [fn for fn in [self.parse_filename(filename) for filename in os.listdir(self.data_dir)
                        if filename.endswith('.json') and filename.startswith(self.slug)
                        and not filename.endswith('fallback.json')] if not fn is None]
        if len(latest_files) > self.max_file_count:
            for file in sorted(latest_files, key=lambda x: int(x['version']))[:-3]:
                os.remove(file['file_path'])

    def parse_filename(self, filename):

        parts = filename.split('.')
        if len(parts) < 3:
            return None
        return {
            'slug': '.'.join(parts[:-2]),
            'version': parts[-2],
            'file_path': os.path.join(self.data_dir, filename)
        }


    def build_file_path(self, version):

        file_name = f'{self.slug}.{version}.json'
        return os.path.join(self.data_dir, file_name)

    def build_data_object(self, content, version, download_time):

        return {
            'content': content,
            'version': version,
            'timestamp': download_time.timestamp()
        }

    def write_data_to_redis(self, data, version, download_time):

        data = self.build_data_object(content=data, version=version, download_time=download_time)
        result = self.redis_client.set_data_with_version(
            keys=[
                self.current_version_key,
                self.data_key(version=version)
            ],
            args=[
                version,
                json.dumps(data),
                self.data_key_prefix,
                self.data_ttl
            ]
        )
        if int(result[0]) == 1:
            return

        data = result[1]
        if not data is None:
            cache_version, download_time, content = self.parse_cache_data(data=data)
            if self.is_larger_than_loaded_version(cache_version):
                self.load_content(data=content,
                                  version=cache_version,
                                  download_time=download_time,
                                  source='cache')

    @property
    def download_in_progress_key(self):
        return f'settings:{self.domain}:{self.slug}:download_in_progress'

    @property
    def current_version(self):
        v = self.redis_client.get(self.current_version_key)
        if v is None:
            return None
        return v.decode()

    @property
    def current_version_key(self):
        return f'settings:{self.domain}:{self.slug}:version'

    def data_key(self, version):
        return f'{self.data_key_prefix}{version}'

    @property
    def data_key_prefix(self):
        return f'settings:{self.domain}:{self.slug}:data:'

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = Session()

            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=['GET', 'POST'],
                respect_retry_after_header=True
            )
            self._session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

        return self._session

    @property
    def current_time(self):
        return pytz.utc.localize(datetime.datetime.utcnow())

    @property
    def current_timestamp(self):
        return int(self.current_time.timestamp())

    @property
    def age(self):
        if self.download_time is None:
            return None
        return self.current_time - self.download_time

    @property
    def too_old(self):
        if self.age is None:
            return False
        return self.age > self.max_age - datetime.timedelta(seconds=self.data_margin_seconds)

    @property
    def is_fallback(self):
        return self.version == self.fallback_version

    def _validate_string_only_array(self, raw):
        if not isinstance(raw, list):
            return False, 'Should be a list'
        if not all(isinstance(r, str) for r in raw):
            return False, 'All entries should be strings'
        if not all(not r.strip() == '' for r in raw):
            return False, 'Empty string not allowed as entry'
        return True, None

    def _validate_dict(self, raw, type=str):
        if not isinstance(raw, dict):
            return False, 'Should be a dictionary'
        if not all(isinstance(k, str) for k in raw):
            return False, 'All keys should be strings'
        if not all(isinstance(v, type) for v in raw.values()):
            return False, f'All values should be {type.__name__}'
        return True, None

    def health(self):

        if self.content is None:
            self.get(version=self.debug_version)

        healthy = False

        if self.is_fallback and not self.fallback_allowed:
            reason = 'Fallback in use'
        elif self.current_time > self.download_time + self.max_age:
            reason = 'Settings too old'
        else:
            healthy = True
            reason = None

        d = {
            'healthy': healthy,
            'slug': self.slug,
            'load_time': self.load_time.isoformat(),
            'download_time': self.download_time.isoformat(),
            'age': str(self.age),
            'max_age': str(self.max_age),
            'allow_fallback': self.fallback_allowed,
            'fallback': self.is_fallback,
            'source': self.source
        }
        if not healthy:
            d.update({'reason': reason})
        return d

