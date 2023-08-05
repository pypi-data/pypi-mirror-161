import functools
import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from py_fastapi_logging.formatters.colored import ColoredLogFormatter
from py_fastapi_logging.formatters.json import JSONLogFormatter
from py_fastapi_logging.formatters.simple import SimpleLogFormatter
from py_fastapi_logging.utils.extra import set_extra_to_environ


class LogConfigure:
    DEFAULT_OUTPUTS = "json,stderr"

    FORMAT_MAP = {"console": "stderr"}

    def __init__(
        self,
        app_name=None,
        filename=None,
        level=None,
        rotate_mb=None,
        rotate_when=None,
        backup_count=7,
        json_multiline=False,
        request_id_support=True,
        log_output=None,
        colored=True,
        log_dir=None,
        cleanup=False,
        exclude_fields=None,
    ):
        self.app_name = app_name
        self._level = level
        self.rotate_mb = rotate_mb
        self.rotate_when = rotate_when
        self.backup_count = backup_count
        self.json_multiline = json_multiline
        self._log_output = log_output
        self._colored = colored
        self._log_dir = log_dir
        self._filename = pathlib.Path(filename) if filename else None
        self.request_id_support = request_id_support
        self._apply_suffix = False
        self.cleanup = cleanup
        self.exclude_fields = exclude_fields

    @property
    def base_app_name(self):
        return self.app_name.split(".", 1)[0]

    @functools.cached_property
    def directory(self):
        log_dir = os.environ.get("LOG_DIR")
        if log_dir:
            return pathlib.Path(log_dir)

        if self._filename and self._filename.is_absolute():
            directory = self._filename.parent
            return directory

        return pathlib.Path("/var/log/", self.base_app_name)

    def get_filename(self, suffix):
        if self._filename:
            filename = self._filename
        else:
            filename = os.environ.get("LOG_FILENAME", f"{self.base_app_name}.log")
        filename = self.directory / filename
        if self._apply_suffix:
            filename.with_suffix(suffix)

        self._apply_suffix = True
        return filename

    def get_exclude_fields(self):
        if self.exclude_fields:
            return self.exclude_fields
        else:
            return os.environ.get("LOG_EXCLUDE_FIELDS", "").split(",")

    def _get_file_handler(self, suffix):
        filename = self.get_filename(suffix)
        if self.rotate_mb:
            handler = RotatingFileHandler(
                filename,
                maxBytes=self.rotate_mb * 1024 * 1024,
                backupCount=self.backup_count,
                encoding="utf-8",
            )

        elif self.rotate_when:
            handler = TimedRotatingFileHandler(
                filename,
                when=self.rotate_when,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        else:
            handler = logging.FileHandler(filename, encoding="utf-8")
        return handler

    def get_handler(self, name):
        if name == "simple":
            handler = self._get_file_handler(".txt")
            formatter = SimpleLogFormatter()
            handler.setFormatter(formatter)
        elif name == "json-stdout":
            handler = logging.StreamHandler()
            formatter = JSONLogFormatter()
            handler.setFormatter(formatter)
        elif name == "json":
            handler = self._get_file_handler(".json")
            formatter = JSONLogFormatter()
            handler.setFormatter(formatter)
        elif name == "stderr":
            handler = logging.StreamHandler()
            formatter = ColoredLogFormatter()
            handler.setFormatter(formatter)
        else:
            raise ValueError(f"unknown handler type: '{name}'")

        return handler

    @property
    def level(self):
        return os.environ.get("LOG_LEVEL", self._level or "INFO").upper()

    def normalize_format_names(self, names: str):
        names = names.lower().split(",")
        return [self.FORMAT_MAP.get(name, name) for name in names]

    @property
    def formats(self):
        if self._log_output:
            names = self._log_output
        else:
            names = os.environ.get("LOG_OUTPUT") or os.environ.get("LOG_FORMAT")
        if not names:
            names = self.DEFAULT_OUTPUTS
        return self.normalize_format_names(names)

    def get_handlers(self, names):
        handlers = [self.get_handler(name) for name in names]
        return handlers

    @property
    def default_logger_level(self):
        level = os.environ.get("LOGGING_DEFAULT_LEVEL") or os.environ.get("LOG_DEFAULT_LEVEL")
        if level:
            level = level.upper()
        return level

    @property
    def default_logger_output(self):
        return os.environ.get("LOGGING_DEFAULT_HANDLER") or os.environ.get("LOG_DEFAULT_OUTPUT")


def _init_logger(config: LogConfigure):
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]

    if config.cleanup:
        for logger in loggers:
            for h in logger.handlers[:]:
                logger.removeHandler(h)
                h.close()

    config.directory.mkdir(exist_ok=True)

    handlers = config.get_handlers(config.formats)

    logging.basicConfig(handlers=handlers, level=config.level)
    set_extra_to_environ("progname", config.app_name)


def init_logger(app_name: str, level: str = "DEBUG"):
    return _init_logger(LogConfigure(app_name=app_name, cleanup=True, level=level))
