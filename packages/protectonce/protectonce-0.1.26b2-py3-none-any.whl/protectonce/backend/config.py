import json
import os
from ..utils import constants
import base64
from urllib.parse import urlparse
from ..utils.logger import Logger
logger = Logger()


class BackendConfig:
    _client_id = None
    _token = None
    _endpoint = None
    _port = None
    _protocol = None

    @classmethod
    def reload(cls):
        cls._set_config()

    @classmethod
    def get_client_id(cls):
        return cls._client_id

    @classmethod
    def get_token(cls):
        return cls._token

    @classmethod
    def get_endpoint(cls):
        return cls._endpoint

    @classmethod
    def get_port(cls):
        return cls._port

    @classmethod
    def get_protocol(cls):
        return cls._protocol

    @classmethod
    def set_config(cls):
        try:
            config_file = cls._get_config_file_path()
            temp_data = open(config_file)
            config = json.load(temp_data)
            cls._parse_token(config)

        except Exception as e:
            logger.info() and logger.write(
                "Failed to read config file. Falling back to environment variables: " + str(e))
            cls._client_id = os.getenv(
                constants.BACKEND_REST_API_CLIENT_ID_ENV, '')
            cls._token = os.getenv(constants.BACKEND_REST_API_TOKEN_ENV, '')
            cls._endpoint = os.getenv(constants.BACKEND_REST_API_URL_ENV, '')
            cls._port = os.getenv(constants.BACKEND_REST_API_PORT_ENV, '')

    @classmethod
    def _parse_token(cls, token_JSON):
        token = token_JSON.get(
            constants.PROTECT_ONCE_CONFIG_TOKEN_BASE_KEY, {})
        config = json.loads(json.loads(
            base64.b64decode(token).decode("utf-8")))
        cls._client_id = config.get(
            constants.PROTECT_ONCE_CONFIG_CLIENT_ID_KEY, "")
        cls._token = config.get(constants.PROTECT_ONCE_CONFIG_TOKEN_KEY, "")
        cls._endpoint = config.get(
            constants.PROTECT_ONCE_CONFIG_ENDPOINT_KEY, "")
        cls._port = config.get(
            constants.PROTECT_ONCE_CONFIG_ENDPOINT_PORT_KEY, None)

    @classmethod
    def get_config_file_path(cls):
        file_env = os.getenv(constants.PROTECT_ONCE_CONFIG_FILE_ENV, None)
        if file_env:
            return file_env

        return os.path.join(os.getcwd(), 'protectOnce.json')

    @classmethod
    def remove_protocol(cls):
        parsed_URL = urlparse(cls._endpoint)
        if parsed_URL.netloc:
            cls._endpoint = parsed_URL.netloc

        cls._protocol = parsed_URL.scheme
