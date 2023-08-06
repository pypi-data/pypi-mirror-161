from requests.sessions import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth

from python_grains.utils import search_obj_from_array

DEFAULT_PATH = '/pseudonyms/'

class AliassingClient(object):

    alias_postfix = 'Alias'

    def __init__(self,
                 hostname,
                 username,
                 password,
                 scheme='https',
                 path=None,
                 retry=3,
                 timeout=5):

        self.hostname = hostname
        self.scheme = scheme
        self.path = path or DEFAULT_PATH
        self.username = username
        self.password = password
        self.default_retry = retry
        self.default_timeout = timeout

    def get_from_service_external(self,
                                  by_alias,
                                  by_input,
                                  timeout=None,
                                  create=True):

        result = {}

        if by_alias:

            r = self.http_session.post(url=self.endpoint,
                                       json=list(by_alias.values()),
                                       auth=self.auth,
                                       params={'create': False},
                                       timeout=timeout or self.default_timeout)

            response = r.json()

            for k,a in by_alias.items():
                _obj = search_obj_from_array(response, 'alias', a['alias'])
                if _obj:
                    if _obj['status'] in (200, 201):
                        result[k] = {**_obj, 'status': 200}
                    else:
                        result[k] = _obj
                else:
                    result[k] = {**a, 'status': 404}

        if by_input:

            r = self.http_session.post(url=self.endpoint,
                                       json=list(by_input.values()),
                                       auth=self.auth,
                                       params={'create': create},
                                       timeout=timeout or self.default_timeout)
            t2 = r.elapsed.total_seconds()
            response = r.json()
            for k, a in by_input.items():
                _obj = search_obj_from_array(response, 'input', a['input'])
                if _obj:
                    if _obj['status'] in (200, 201):
                        result[k] = {**_obj, 'status': 200}
                    else:
                        result[k] = _obj
                else:
                    result[k] = {**a, 'status': 404}

        return result

    def get(self,
            input,
            timeout=None,
            create=False):

        if not input:
            return []
        else:

            to_service = {}
            result = {}
            input = dict(enumerate(input))
            for k, a in input.items():
                to_service[k] = a

            if to_service:
                by_input = {k: r for k, r in to_service.items() if 'input' in r}
                by_alias = {k: r for k, r in to_service.items() if not 'input' in r}

                result = self.get_from_service_external(by_alias=by_alias, by_input=by_input, timeout=timeout, create=create)

        final_result = [None] * (max(input) + 1)
        for k, a in input.items():
            final_result[k] = {k:v for k,v in result.get(k, {**a, 'status': 404}).items() if k in ('input', 'status', 'variable', 'alias')}

        return final_result

    def preprocess_input(self,
                         input):

        return [{'variable': k, 'input': v} for k,v in input.items()]

    def postprocess_output(self,
                           output):

        return {a['variable'] + self.alias_postfix: a['alias'] for a in output if a['status'] in (200, 201)}

    @property
    def auth(self):

        return HTTPBasicAuth(self.username, self.password)

    @property
    def http_session(self):

        if not hasattr(self, '_http_session') or self._http_session is None:
            self._http_session = Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=['GET', 'POST'],
                respect_retry_after_header=True
            )
            self._http_session.mount(self.host, adapter=HTTPAdapter(max_retries=retry_strategy))
        return self._http_session

    @property
    def host(self):
        return f'{self.scheme}://{self.hostname}'

    @property
    def endpoint(self):

        return f'{self.host}{self.path}'
