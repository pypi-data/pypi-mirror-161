import threading
from ...utils.logger import Logger
logger = Logger()

_thread_local_store = threading.local()


def store_property(data):
    try:
        # FIXME: Implement a real cls instead of thread local
        cls_context = getattr(_thread_local_store, 'po_cls_context', {})
        cls_context[data['config']['property']] = data['result']
        _thread_local_store.po_cls_context = cls_context
    except Exception as e:
        logger.info() and logger.write('cls.store_property failed with error : ' + str(e))
        return


def get_property(data):
    try:
        cls_context = getattr(_thread_local_store, 'po_cls_context', {})
        poSessionId = cls_context.get(data['config']['property'], '')
        return {"poSessionId": poSessionId}
    except Exception as e:
        logger.info() and logger.write(' cls.get_property failed with error : ' + str(e))
        return {}
