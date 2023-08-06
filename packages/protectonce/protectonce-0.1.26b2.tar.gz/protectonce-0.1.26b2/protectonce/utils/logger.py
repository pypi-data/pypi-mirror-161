import os

log_levels = {
    'PO_LOG_LEVEL_QUIET': 0,
    'PO_LOG_LEVEL_ERROR': 1,
    'PO_LOG_LEVEL_INFO': 2,
    'PO_LOG_LEVEL_VERBOSE': 3
}


class Logger():

    def __init__(self):
        log_level = os.getenv('PROTECTONCE_LOG_LEVEL', 'error')
        self._set_log_level(log_level)

    def write(self, message):
        if not self._tag:
            return
        print(f"[{self._tag}] {message}")
        self._tag = None

    def error(self):
        return self._should_print(log_levels.get('PO_LOG_LEVEL_ERROR'), 'PROTECTONCE_ERROR')

    def info(self):
        return self._should_print(log_levels.get('PO_LOG_LEVEL_INFO'), 'PROTECTONCE_INFO')

    def debug(self):
        return self._should_print(log_levels.get('PO_LOG_LEVEL_VERBOSE'), 'PROTECTONCE_DEBUG')

    def _should_print(self, log_level, tag):
        if self._log_level < log_level:
            self.tag = None
            return False

        self._tag = tag
        return True

    def _set_log_level(self, log_level):
        self._log_level = log_levels.get('PO_LOG_LEVEL_ERROR')
        if not isinstance(log_level, str):
            return

        lower_log_level = log_level.lower()
        if lower_log_level == "quiet":
            self._log_level = log_levels.get('PO_LOG_LEVEL_QUIET')

        elif lower_log_level == "error":
            self._log_level = log_levels.get('PO_LOG_LEVEL_ERROR')

        elif lower_log_level == "info":
            self._log_level = log_levels.get('PO_LOG_LEVEL_INFO')

        elif lower_log_level == "verbose":
            self._log_level = log_levels.get('PO_LOG_LEVEL_VERBOSE')
