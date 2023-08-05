import json

import requests

from dapi.version import __version__

DEFAULT_LIBRARY_USER_AGENT = f'Dapi Connect Python V{__version__}'
API_HOST = 'https://api.dapi.com'
API_VERSION = 'v2'
API_BASE_URL = f'{API_HOST}/{API_VERSION}'
DD_HOST = 'https://dd.dapi.com'


class DapiRequest(object):
    def __init__(self, client):
        self.client = client

    def _build_authenticated_request_params(self, user_secret, data):
        params = {
            "appSecret": self.client.app_secret,
            "userSecret": user_secret,
            **data
        }
        return params

    def _get_authenticated_request_headers(self, access_token):
        params = {
            "Authorization": f'Bearer {access_token}'
        }
        return params

    def authenticated_request(self, access_token, user_secret, resource_path, post_data={}, ):
        post_data = self._build_authenticated_request_params(
            user_secret, post_data)

        headers = self._get_authenticated_request_headers(access_token)

        return self.post(resource_path, post_data, headers)

    def post(self, resource_path, post_data={}, headers={}, comingFromDD=False):
        url = DD_HOST if comingFromDD else f'{API_BASE_URL}{resource_path}'

        resp = requests.post(url, data=json.dumps(post_data), timeout=self.client.timeout, headers={
            'User-Agent': DEFAULT_LIBRARY_USER_AGENT,
            'Content-Type': 'application/json',
            **headers
        })
        return resp.json()
