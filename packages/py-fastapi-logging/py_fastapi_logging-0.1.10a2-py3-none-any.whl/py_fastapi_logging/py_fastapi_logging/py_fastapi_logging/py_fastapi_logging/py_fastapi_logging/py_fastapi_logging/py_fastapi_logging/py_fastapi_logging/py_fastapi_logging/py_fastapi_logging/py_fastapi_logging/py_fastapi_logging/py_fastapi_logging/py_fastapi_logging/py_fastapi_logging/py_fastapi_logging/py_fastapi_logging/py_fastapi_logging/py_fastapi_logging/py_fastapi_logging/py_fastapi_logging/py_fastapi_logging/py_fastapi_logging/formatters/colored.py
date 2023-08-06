import logging

from py_fastapi_logging.formatters.base import BaseFormatter

COLOR_MAPPING = {
    "INFO": "\33[32m",
    "WARNING": "\33[33m",
    "CRITICAL": "\33[35m",
    "ERROR": "\33[31m",
}


class ColoredLogFormatter(BaseFormatter):
    def _format_log(self, record: logging.LogRecord) -> dict:
        t = self.formatTime(record)
        level = record.levelname
        line = record.lineno
        color = COLOR_MAPPING.get(level) or "\33[34m"  # blue
        default_color = "\33[0m"
        msg = record.getMessage()
        tags = record.__dict__.get("tags", None)
        tags = tags if not tags else " ".join(tags)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        s = f"{color}{t} {level} "

        s += f'{record.__dict__.get("request_id", "")}'
        if tags:
            s += f" {tags}"
        s += f"\n{record.pathname} line {line}{default_color}\n" f"{msg}\n"

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)

        return s
