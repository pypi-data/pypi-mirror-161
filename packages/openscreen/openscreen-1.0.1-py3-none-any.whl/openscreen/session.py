import sys
import time
import re
from urllib.parse import urlencode
from dataclasses import asdict
import requests
from .config import Config


def make_uri(route_segments: list, path_parameters: object):
    url_parts = []
    for segment in route_segments:
        url_parts.append(segment['routePart'])
        if (segment.get('parm')):
            param_value = path_parameters.get(segment['parm'])
            if not param_value:
                raise Exception(f'Openscreen: missing path parameter value for "{segment["parm"]}"')
            url_parts.append(str(param_value))

    url = '/'.join(url_parts)
    if url[0] != '/':
        url = '/' + url
    return url


def to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def from_snake_to_camel(name):
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def t_dict_snake(d):
    if isinstance(d, list):
        return [t_dict_snake(i) if isinstance(i, (dict, list)) else i for i in d]
    return {to_snake(a): t_dict_snake(b) if isinstance(b, (dict, list)) else b for a, b in d.items()}


def t_dict_camel(d):
    if isinstance(d, list):
        return [t_dict_camel(i) if isinstance(i, (dict, list)) else i for i in d]
    return {from_snake_to_camel(a): t_dict_camel(b) if isinstance(b, (dict, list)) else b for a, b in d.items()}


class Session(object):
    def __init__(self, access_key, access_secret, config_name, timeout=30, **kwargs):
        self.access_key = access_key
        self.access_secret = access_secret
        self.timeout = timeout
        self._apiKeyId = None
        self.exp = 0
        self.config = None
        self.authenticated = False
        # self._token = None
        # self._refresh_token = None
        self.config_name = config_name
        self.debug_request = False
        if kwargs.get('debug') or kwargs.get('debugRequest'):
            self.debug_request = True

        self._fetch_config()
        self.request_session = requests.session()
        self.base_url = self.config['endpoint']
        self.timeout = self.config['axios']['timeout']
        self.request_session.__setattr__('timeout', self.timeout)
        self.request_session.headers = {'User-Agent': 'Python/3.10', 'Content-Type': 'application/json'}

    def authenticate(self):
        session = self.getRequestsSession()
        if self.exp > time.time():
            # the current token is not expired yet
            return

        elif self.exp != 0:
            # that means token expired
            res = session.post(f'{self.base_url}/auth/session/refresh')
            if res.status_code != 200:
                self.authenticated = False
                print(f'Openscreen AUTH: failed to refresh  key {self.access_key}, exiting')
                self.__delete__()
                return
        # means exp == 0
        res = session.post(f'{self.base_url}/auth/session', json={
            'key': self.access_key,
            'secret': self.access_secret
        })

        if res.status_code != 200:
            self.authenticated = False
            print(f'Openscreen AUTH: failed to authorize  key {self.access_key}')
            self.__delete__()
            return

        self.authenticated = True
        data = res.json()
        self._apiKeyId = data['apiKeyId']
        self.exp = data['expires']

    def _refresh(self):
        session = self.getRequestsSession()
        res = session.post(f'{self.base_url}/auth/session/refresh')

        if res.status_code != 200:
            self.authenticated = False
            print(f'Openscreen AUTH: failed to refresh  key {self.access_key}, please restart to login again')
            self.__delete__()
            return

        self.authenticated = True
        data = res.json()
        self.exp = data['expires']

    def _fetch_config(self):
        config_instance = Config(config_name=self.config_name, debug_request=self.debug_request)
        config_instance.loadConfig()
        self.config = config_instance.config

    def __delete__(self):
        print('Openscreen: Closing Openscreen connection')
        self.request_session.close()
        sys.exit(0)

    def go(self, method, route_segments: list, query_parameters, path_parameters, request_body, response_body_class):
        method = method.lower()
        if request_body and type(request_body) != dict:
            request_body = asdict(request_body)
        if(request_body): request_body = t_dict_camel(request_body)
        self.authenticate()
        path = make_uri(route_segments, path_parameters)
        if query_parameters:
            query_parameters = urlencode(query_parameters)
            target_path = self.base_url + path + '?' + query_parameters
        else:
            target_path = self.base_url + path
        res = None
        if method == 'get':
            res = self._get_request(target_path)
        elif method == 'post':
            res = self._post_request(target_path, request_body)
        elif method == 'patch':
            res = self._patch_request(target_path, request_body)
        elif method == 'delete':
            res = self._delete_request(target_path)
        else:
            print(f'Openscreen: Got an invalid method - {method}')
            return

        if res.status_code == 400:
            # validation error
            raise TypeError(res.json())
        elif res.status_code == 500:
            # internal server error
            raise Exception(res.json())
        elif res.status_code == 403:
            raise PermissionError('Failed due to invalid permissions', res.json())
        elif res.status_code == 404:
            raise ModuleNotFoundError(res.json())

        elif res.status_code == 204:
            return None
        else:
            # convert keys of res.json to snake_case
            return response_body_class(**t_dict_snake(res.json()))

    def _get_request(self, target_path):
        res = self.request_session.request('GET', target_path)
        return res

    def _post_request(self, target_path, request_body):
        res = self.request_session.request('POST', target_path, json=request_body)
        return res

    def _patch_request(self, target_path, request_body):
        res = self.request_session.request('PATCH', target_path, json=request_body)
        return res

    def _delete_request(self, target_path):
        res = self.request_session.request('DELETE', target_path)
        return res

    def getRequestsSession(self):
        return self.request_session

    def getApiKeyId(self):
        return self._apiKeyId
