import logging

from py_fastapi_logging.utils.extra import get_extra_from_environ


class BaseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        record: logging.LogRecord = self._update_extra(record)
        log: str = self._format_log(record)
        return log

    def _update_extra(self, record: logging.LogRecord) -> logging.LogRecord:
        extra = get_extra_from_environ()
        for extra_key, extra_value in extra.items():
            if not hasattr(record, extra_key):
                setattr(record, extra_key, extra_value)
        return record
