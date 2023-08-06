import datetime
import logging
import traceback

import orjson

from py_fastapi_logging.formatters.base import BaseFormatter
from py_fastapi_logging.schemas.base import BaseJsonLogSchema
from py_fastapi_logging.utils.extra import get_env_extra


class JSONLogFormatter(BaseFormatter):
    def __init__(self, fmt=None, datefmt=None, style="%", validate=True, multi_line=None):
        self.multi_line = multi_line
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self._skip_extra = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "payload",
            "function_name",
            "function_version",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "project_name" "thread",
            "threadName",
            "processName",
            "process",
            "request_id",
            "progname",
            "tags",
        }

    def get_extra(self, record):
        extra = {name: value for name, value in record.__dict__.items() if name not in self._skip_extra}
        return extra

    @staticmethod
    def _default_to_str(value):
        return str(value)

    def _format_log(self, record: logging.LogRecord) -> dict:
        payload = {"message": record.getMessage()}
        now = datetime.datetime.fromtimestamp(record.created).astimezone().replace(microsecond=0).isoformat()

        json_log_fields = BaseJsonLogSchema(
            timestamp=now,
            level=record.levelname,
        )
        if hasattr(record, "tags"):
            json_log_fields["tags"] = record.tags

        for key in get_env_extra().keys():
            if hasattr(record, key):
                json_log_fields[key] = getattr(record, key)
            elif key == "progname":
                json_log_fields[key] = record.module

        aux = {
            "module": record.module,
            "lineno": record.lineno,
            "func_name": record.funcName,
            "process": record.process,
            "thread_name": record.threadName,
            "logger_name": record.name,
        }
        payload["aux"] = aux

        if record.args:
            payload["args"] = record.args
        extra = self.get_extra(record)
        if extra:
            payload["extra"] = extra
        try:
            if record.exc_info:
                payload["exception"] = {
                    "class":  record.exc_info.__class__.__name__,
                    "message":  str(record.exc_info),
                    "backtrace": traceback.format_exception(*record.exc_info)
                }
        except Exception:
            payload["exception"] = traceback.format_exception(*record.exc_info)

        if record.exc_text:
            payload["exception"] = record.exc_text
        json_log_fields["payload"] = payload

        option = orjson.OPT_UTC_Z
        if self.multi_line:
            option |= orjson.OPT_INDENT_2

        try:
            packed = orjson.dumps(json_log_fields, default=self._default_to_str, option=option)
        except Exception as e:
            m = {str(k): str(v) for k, v in json_log_fields.items()}
            m["failed_dump"] = str(e)
            packed = orjson.dumps(m, default=self._default_to_str, option=option)
        return packed.decode("utf-8")
