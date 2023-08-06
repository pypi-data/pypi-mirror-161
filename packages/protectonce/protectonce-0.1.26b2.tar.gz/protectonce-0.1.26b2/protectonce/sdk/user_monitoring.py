from ..core_interface import invoke_core_method
from ..rules.handlers import cls
from ..rules.handlers import http_server
from ..utils.logger import Logger
logger = Logger()

data = {
    "config": {
        "property": "__poSessionId"
    }
}


def __get_session_id():
    return cls.get_property(data)


def report_signup(user_name):
    """input parameters user_name as string"""
    if not isinstance(user_name, str):
        logger.info() and logger.write('protectonce.report_signup: ' +
                                       str(user_name) + ' should be string')
        return
    try:
        po_session_id = __get_session_id().get('poSessionId', '')
        signup_data = {"data": {
            "poSessionId": po_session_id,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.storeSignUpData", signup_data)
        logger.info() and logger.write('Result_actions== ' + str(result))
        result["config"] = data["config"]
        http_server.cancel_request(result)
    except Exception as e:
        logger.error() and logger.write(
            'protectonce.report_signup: Error occured while handling signup data : ' + str(e))


def report_login(status, user_name):
    """input parameters status as boolean 'True' or 'False' and user_name as string"""

    if not isinstance(user_name, str) or not isinstance(status, bool):
        logger.error() and logger.write('protectonce.report_login: ' + str(user_name) +
                                        ' and ' + str(status) + ' should be boolean either True or False')
        return

    try:
        po_session_id = __get_session_id().get('poSessionId', '')
        login_data = {"data": {
            "poSessionId": po_session_id,
            "success": status,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.storeLoginData", login_data)
        result["config"] = data["config"]
        http_server.cancel_request(result)
    except Exception as e:
        logger.error() and logger.write(
            'protectonce.report_login: Error occured while handling login data : ' + str(e))


def report_auth(user_name, traits=None):
    """input parameters user_name as string traits is optional"""
    if not isinstance(user_name, str):
        logger.info() and logger.write('protectonce.report_auth: ' +
                                       str(user_name) + ' should be string')
        return
    try:
        po_session_id = __get_session_id().get('poSessionId', '')
        auth_data = {"data": {
            "poSessionId": po_session_id,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.identify", auth_data)
        result["config"] = data["config"]
        http_server.cancel_request(result)
    except Exception as e:
        logger.error() and logger.write(
            ' protectonce.report_auth: Error occured while handling authentication data : ' + str(e))


def is_user_blocked(user_name, traits=None):
    """input parameters user_name as string traits is optional"""
    if not isinstance(user_name, str):
        logger.info() and logger.write('protectonce.is_user_blocked: ' +
                                       str(user_name) + ' should be string')
        return
    try:
        po_session_id = __get_session_id().get('poSessionId', '')
        user_data = {"data": {
            "poSessionId": po_session_id,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.checkIfBlocked", user_data)
        result["config"] = data["config"]
        http_server.cancel_request(result)
    except Exception as e:
        logger.error() and logger.write(
            'protectonce.is_user_blocked: Error occured while checking is user blocked : ' + str(e))
