from . import core_interface
from .rules.rules_manager import RulesManager
import atexit
from .login import rules_sync as heartbeat


def start():
    rules = core_interface.login()
    # TODO features and hooks will be received from core need to process features
    if isinstance(rules, dict):
        rules_manager = RulesManager(rules)
        rules_manager.apply_rules()


@atexit.register
def stop():
    if heartbeat.heartbeat_thread.is_alive():
        heartbeat.heartbeat_thread.cancel()
    heartbeat.thread_should_stop = True
    heartbeat.sync_rules()
    core_interface.stop()


start()
