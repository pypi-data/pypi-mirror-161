from .config import BackendConfig
import base64


class APIToken:
    def __init__(self):
        self._access_token = None
        self._refresh_token = None

    def update(self, auth):
        self._access_token = auth.access_token
        self._refresh_token = auth.refresh_token

    def get_auth_header(self):
        if self._access_token == None:
            return self._get_basic_auth_header()

        return self._get_bearer_token()

    def get_refresh_token(self):
        return self._refresh_token

    def _get_basic_auth_header(self):
        temp_header = BackendConfig.get_client_id() + ":" + BackendConfig.get_token()
        return "Basic "+base64.b64encode(bytes(temp_header, 'utf-8')).decode("utf-8")

    def _get_bearer_token(self):
        return "Bearer " + self._access_token
