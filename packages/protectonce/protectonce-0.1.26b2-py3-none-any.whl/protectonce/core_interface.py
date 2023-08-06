from ctypes import c_char_p
import sys
from protectonce_native.runtimes.python.protect_once_py_interface import (
    ProtectOnceInterface,
)
import json
import pkg_resources
import os
import hashlib
import socket
from .login.login_sync import Login
from .utils.logger import Logger

logger = Logger()

po_interface = ProtectOnceInterface()
po_interface.init_core()


def invoke_core_method(function_name, data):
    str_data = json.dumps(data)
    result, out_data_type, out_data_size, mem_buffer_id = po_interface.invoke(
        function_name, str_data, len(str_data))
    if result:
        val = c_char_p(result).value
        result = json.loads(val.decode('utf-8'))
    else:
        logger.info() and logger.write(str(function_name) + ' method returned None')
    po_interface.release(mem_buffer_id)
    return result, out_data_type, out_data_size


def login():
    runtime_version = "{0}.{1}.{2}".format(
        str(sys.version_info.major),
        str(sys.version_info.minor),
        str(sys.version_info.micro),
    )

    packages = []

    for package in pkg_resources.working_set:
        packages.append({
            "name": package.project_name,
            "version": package.version,
            "vendor": package.platform,
            "type": 'static'
        })

    current_working_dir = os.getcwd()
    last_index_forwardslash = current_working_dir.rfind(os.sep)
    root_app_name = current_working_dir[last_index_forwardslash+1:]

    login_data = {
        "runtime": "python",
        "runtimeVersion": runtime_version,
        "bom": packages,
        # os.uname()[1] doesn't work on windows
        "hostname": socket.gethostname(),
        "workLoadId": _get_workload_id(),
        "appName": root_app_name
    }
    login = Login()
    core_status = login.initialise(login_data)
    return core_status


def _get_workload_id():
    try:
        if os.environ.get('PROTECTONCE_WORKLOAD_ID'):
            return os.environ['PROTECTONCE_WORKLOAD_ID']
        hashof = str(socket.gethostname()) + str(sys.argv[0])
        hash_object = hashlib.sha1(hashof.encode("utf-8"))

        return hash_object.hexdigest()
    except Exception as e:
        logger.info() and logger.write(
            '_get_workload_id failed returning DEFAULT_WORKLOAD with error ' + str(e))
    return 'DEFAULT_WORKLOAD'


def stop():
    po_interface.shutdown_core()
