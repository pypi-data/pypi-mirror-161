from ctypes import c_char_p
from ...core_interface import po_interface
from orjson import orjson as json
from ...utils.logger import Logger
logger = Logger()


class CoreHandler(object):
    def __init__(self, rule, data) -> None:
        super(CoreHandler, self).__init__()
        self._method = data.get('method', '')
        self._rule = rule
        self._config = data.get('config', {})

    def handle_callback(self, method_data, data) -> bool:
        core_data = {
            'args': data['args'],
            'data': data['result'],
            'context': self._rule.context,
            'config': self._config
        }

        str_data = json.dumps(core_data, default=lambda o: {})
        result, out_data_type, out_data_size, mem_buffer_id = po_interface.invoke(
            self._method, str_data, len(str_data))

        if result:
            val = c_char_p(result).value
            result = val.decode('utf-8')
        else:
            logger.info() and logger.write(
                str({self._method}) + 'method returned None')
        po_interface.release(mem_buffer_id)

        try:
            return json.loads(result)
        except ValueError as e:
            return result
