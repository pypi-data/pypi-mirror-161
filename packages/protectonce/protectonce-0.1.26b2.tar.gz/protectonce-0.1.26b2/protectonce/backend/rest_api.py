import json
import os
from .config import BackendConfig
from ..utils import constants
import requests
from .token import APIToken
from ..utils.logger import Logger


class RestAPI:
    def __init__(self, path, data):
        self.logger = Logger()
        if path == '/login':
            BackendConfig.set_config()
            BackendConfig.remove_protocol()
        self._api_token = APIToken()
        self._path = path
        self._data = ''
        try:
            self._data = json.dumps(data)

        except Exception as e:
            self._data = ''

    def url(self):
        return BackendConfig.get_endpoint()

    def port(self):
        port = BackendConfig.get_port()
        if port:
            return port
        return ''

    def protocol(self):
        return BackendConfig.get_protocol()

    def get_post_options(self):
        post_opts = {
            'hostname': self.url(),
            'path': self._path,
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json',
                'Content-Length': len(self._data),
                'Authorization': self._api_token.get_auth_header()
            }
        }

        if self.port():
            post_opts['port'] = self.port()

        if(self._api_token.get_refresh_token()):
            post_opts['headers'][constants.BACKEND_REST_API_REFRESH_TOKEN_HEADER] = self._api_token.get_refresh_token()

        return post_opts

    def get_protocol(self):
        return self.protocol() + '://' if self.protocol() else 'https://'

    def get_port(self):
        return ':' + self.port()

    def build_request_URL(self):
        return self.get_protocol() + self.url() + self.get_port() + self._path

    def get_request_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(self._data)),
            'Authorization': self._api_token.get_auth_header()
        }

        if self._api_token.get_refresh_token():
            headers[constants.BACKEND_REST_API_REFRESH_TOKEN_HEADER] = self._api_token.get_refresh_token()

        return headers

    def post(self):
        self.logger.debug() and self.logger.write(
            'REST API post: Sending request to: ' + str(self.url()))
        if not self.url():
            return {'data': '{}', 'statusCode': 200}

        request_URL = self.build_request_URL()
        self.logger.debug() and self.logger.write(
            'REST API post: RequestUrl: ' + str(request_URL))

        response = ''

        response = requests.post(
            request_URL, headers=self.get_request_headers(), data=self._data, timeout=10)

        if response != None and response.status_code != 200:
            return {'data': '{}', 'statusCode': response.status_code}

        rules_data = {'data': response.content.decode(
            'utf-8'), 'statusCode': response.status_code}

        return rules_data
