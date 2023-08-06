from ..utils import constants
from ..backend.rest_api import RestAPI
from ..utils.config import Config
from .. import core_interface
from . import rules_sync
from ..utils.logger import Logger
import json


class Login:
    def __init__(self):
        self.logger = Logger()

    def initialise(self, runtime_info):
        resp = self._login_sync(runtime_info)
        return resp

    def _login_sync(self, runtime_info):
        try:
            Config.set_runtime_info(runtime_info)
            rest_api = RestAPI(constants.REST_API_LOGIN, Config.get_info())

            backend_rules_data = rest_api.post()
            self.logger.info() and self.logger.write(
                'Login returned: ' + json.dumps(backend_rules_data))
            rules_data = {
                'data': backend_rules_data
            }

            results, out_data_type, out_data_size = core_interface.invoke_core_method(
                "coreInterface.getRuntimeRules", rules_data)
            if results.get('appDeleted', False):
                self.logger.info() and self.logger.write(
                    '_login_sync Deletion triggered from PO dashboard, this app is no longer protected.')
                return {}

            rules_sync.start_heartbeat_timer()
            return results

        except Exception as e:
            self.logger.error() and self.logger.write(
                '_login_sync Failed to call login with error: ' + str(e))
            return []
