from ..utils import constants
from ..backend.rest_api import RestAPI
from .. import core_interface
from ..utils.config import Config
import json
import threading
from ..utils.logger import Logger
from ..bom.bom_handler import BomHandler
logger = Logger()
thread_should_stop = False


def start_heartbeat_timer():
    if thread_should_stop:
        return
    sync_rules()
    global heartbeat_thread
    heartbeat_thread = threading.Timer(
        Config.sync_interval(), start_heartbeat_timer)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()


def stop_heartbeat_timer(status_code):
    if status_code != constants.APP_DELETE_STATUS_CODE:
        return

    logger.info() and logger.write(
        'Deletion triggered from PO dashboard, this app is no longer protected.')
    global thread_should_stop
    thread_should_stop = True


def sync_rules():
    try:
        heart_beat_info, out_data_type, out_data_size = core_interface.invoke_core_method(
            "coreInterface.getHeartbeatInfo", "")

        info = Config.get_info()
        heart_beat_info['agentId'] = info.get('agentId', '')

        heart_beat_info['workLoadId'] = info.get('workLoadId', '')

        heart_beat_info['dynamicBom'] = BomHandler.process_dynamic_bom()

        rest_api = RestAPI(constants.REST_API_HEART_BEAT, heart_beat_info)

        logger.debug() and logger.write(
            'Sending heartbeat to backend: ' + json.dumps(heart_beat_info))
        backend_rules_data = rest_api.post()

        logger.info() and logger.write(
            'Heartbeat returned : ' + json.dumps(backend_rules_data))
        rules_data = {
            'data': backend_rules_data
        }

        results, out_data_type, out_data_size = core_interface.invoke_core_method(
            "coreInterface.getRuntimeRules", rules_data)

        if results.get('appDeleted', False):
            logger.info() and logger.write(
                'sync_rules Deletion triggered from PO dashboard, this app is no longer protected.')
            stop_heartbeat_timer(constants.APP_DELETE_STATUS_CODE)
            return {}

        stop_heartbeat_timer(backend_rules_data.get('statusCode', ''))

        return results

    except Exception as e:
        logger.error() and logger.write(
            'sync_rules Failed to send heartbeat with error: ' + str(e))
        return []
