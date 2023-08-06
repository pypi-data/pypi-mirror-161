from requests.sessions import Session
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import exceptions as requests_exceptions
import urllib3
import pytz
import datetime
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HEC_SOURCE = 'python-grains-splunk-client'
DEFAULT_HEC_SOURCE_TYPE = '_json'
DEFAULT_HEC_TIMEOUT = 1.0

class SplunkError(Exception): pass

class SplunkTimeout(SplunkError): pass
class SplunkInvalidConfig(SplunkError): pass
class SplunkInvalidInput(SplunkError): pass

class SplunkClient(object):

    def __init__(self,
                 hostname,
                 scheme='https',
                 management_port=8089,
                 hec_port=8088,
                 hec_token=None,
                 hec_source=None,
                 hec_source_type=None,
                 hec_timeout=None,
                 hec_omit_port=False):

        self.hostname = hostname
        self.scheme = scheme
        self.management_port = management_port
        self.hec_port = hec_port
        self.hec_token = hec_token
        self.hec_omit_port = hec_omit_port
        self._hec_timeout = hec_timeout
        self._hec_source = hec_source
        self._hec_source_type = hec_source_type


    def hec_send(self,
                 events,
                 index,
                 timestamp=None,
                 source=None,
                 sourcetype=None):

        if not isinstance(events, list):
            raise ValueError('events must be a list')

        payloads = [self.splunk_payload(event,
                                        index,
                                        timestamp=timestamp,
                                        source=source,
                                        sourcetype=sourcetype)
                    for event in events]

        return self.hec_send_payloads(payloads)

    def hec_send_payloads(self, payloads):

        payload_strings = [self.splunk_payload_string(payload) for payload in payloads]
        data = ''.join(payload_strings)

        try:
            r = self.http_session.post(self.hec_endpoint,
                                       data=data,
                                       timeout=self.hec_timeout,
                                       headers={'Authorization': self.hec_auth_header})
        except requests_exceptions.Timeout:
            raise SplunkTimeout
        if r.status_code == 200:
            return []
        else:
            return [r.content]

    def splunk_payload(self, event, index, timestamp=None, source=None, sourcetype=None):

        if timestamp is None:
            timestamp = pytz.utc.localize(datetime.datetime.utcnow()).timestamp()
        else:
            if not isinstance(timestamp, (float, int)):
                raise ValueError('timestamp must be a float')

        return {
            'time': timestamp,
            'index': index,
            'source': source or self.hec_source,
            'sourcetype': sourcetype or self.hec_sourcetype,
            'event': event
        }

    def splunk_payload_string(self,
                       event):

        return json.dumps(event)

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
    def hec_endpoint(self):
        if self.hec_omit_port:
            return f'{self.host}/services/collector/event'
        return f'{self.host}:{self.hec_port}/services/collector/event'

    @property
    def host(self):
        return f'{self.scheme}://{self.hostname}'

    @property
    def hec_auth_header(self):
        if self.hec_token is None:
            raise SplunkInvalidConfig('No HEC token given')
        return f'Splunk {self.hec_token}'

    @property
    def hec_source(self):
        return self._hec_source or DEFAULT_HEC_SOURCE

    @property
    def hec_sourcetype(self):
        return self._hec_source_type or DEFAULT_HEC_SOURCE_TYPE

    @property
    def hec_timeout(self):
        return self._hec_timeout or DEFAULT_HEC_TIMEOUT


