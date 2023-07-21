import os
import re
import sys
import json
import string
import random
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler
from celery.signals import setup_logging


def random_string(length=8):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


class Colors:
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    PURPLE = "\x1b[35m"
    LIGHT_BLUE = "\x1b[36m"
    GREY = "\x1b[37m"

    BLACK_BACKGROUND = "\x1b[40m"
    RED_BACKGROUND = "\x1b[41m"
    GREEN_BACKGROUND = "\x1b[42m"
    YELLOW_BACKGROUND = "\x1b[44m"
    BLUE_BACKGROUND = "\x1b[44m"
    PURPLE_BACKGROUND = "\x1b[45m"
    LIGHT_BLUE_BACKGROUND = "\x1b[46m"
    GREY_BACKGROUND = "\x1b[47m"

    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    UNDERLINE = "\x1b[4m"
    REVERSE = "\x1b[7m"
    DEL_LINE = "\x1b[9m"
    BOLD_UNDERLINE = "\x1b[21m"
    BOX = "\x1b[51m"


class ColorizedFormatter(logging.Formatter):
    colors = [Colors.GREEN, Colors.BLUE, Colors.PURPLE, Colors.YELLOW, Colors.RED, Colors.GREY]
    level_to_color = {
        logging.DEBUG: Colors.GREEN,
        logging.INFO: Colors.BLUE,
        logging.WARNING: Colors.RED,
        logging.ERROR: f"{Colors.BOLD}{Colors.RED}",
        logging.CRITICAL: f"{Colors.BOLD}{Colors.BLACK}{Colors.RED_BACKGROUND}",
    }
    field_to_color = {
        "asctime": Colors.BLUE,
        "module": Colors.BLUE
    }

    def __init__(self, fmt: str, datefmt=None, style='%', **kwargs):
        super(ColorizedFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style, **kwargs)

        self.level_to_formatter = {}

        def add_color_formatter(level):
            level_color = ColorizedFormatter.level_to_color[level]
            _format = fmt

            # process level color
            for fld in ["levelname", "levelno"]:
                _pattern = "(%\(" + fld + "\).*?s)"
                pattern = "({" + fld + ".*?})"
                _format = re.sub(_pattern, f"{level_color}\\1{Colors.RESET}", _format, count=1)
                _format = re.sub(pattern, f"{level_color}\\1{Colors.RESET}", _format, count=1)

            # process fields color
            for fld, field_color in ColorizedFormatter.field_to_color.items():
                _pattern = "(%\(" + fld + "\).*?s)"
                pattern = "({" + fld + ".*?})"
                _format = re.sub(_pattern, f"{field_color}\\1{Colors.RESET}", _format, count=1)
                _format = re.sub(pattern, f"{field_color}\\1{Colors.RESET}", _format, count=1)

            self.level_to_formatter[level] = logging.Formatter(_format, datefmt=datefmt, style=style, **kwargs)

        add_color_formatter(logging.DEBUG)
        add_color_formatter(logging.INFO)
        add_color_formatter(logging.WARNING)
        add_color_formatter(logging.ERROR)
        add_color_formatter(logging.CRITICAL)

    def formatMessage(self, record):
        if isinstance(record.msg, dict) and self.is_serializable(record.msg):
            record.msg = json.dumps(record.msg, indent=4, ensure_ascii=False)

        _formatter = self.level_to_formatter.get(record.levelno)
        _msg = record.msg
        _args = record.args
        self.rewrite_record(record)
        s = _formatter.format(record)
        indent = ' ' * self.get_header_length(s, record)
        head, *trailing = s.splitlines(True)
        s = head + ''.join(indent + line for line in trailing)
        record.msg = _msg
        record.args = _args
        return s

    def rewrite_record(self, record: logging.LogRecord):
        if not record.args: return

        msg = record.msg
        if isinstance(record.args, tuple):
            args = []
            arg_int = []
            for index, arg in enumerate(record.args):
                color = self.colors[index % len(self.colors)]
                if isinstance(arg, int):
                    _int = random_string()
                    arg_int.append(_int)
                    msg = re.sub("%d", f"{color}{Colors.UNDERLINE}{_int}{Colors.RESET}", msg, count=1)
                    args.append(arg)
                else:
                    args.append(f"{color}{arg}{Colors.RESET}")

            for _int in arg_int:
                msg = re.sub(_int, "%d", msg, count=1)

            record.msg = msg % tuple(args)

        if isinstance(record.args, dict):
            index = 0
            arg_dict = record.args.copy()
            int_color = {}
            for key, value in record.args.items():
                color = self.colors[index % len(self.colors)]
                if isinstance(value, str):
                    arg_dict[key] = f"{color}{value}{Colors.RESET}"
                elif isinstance(value, int):
                    int_color[key] = color
                index += 1

            for key, value in int_color.items():
                _key = re.search("%\({}\).*?d".format(key), msg).group(0)
                pattern = _key.replace("(", "\(").replace(")", "\)")
                msg = re.sub(pattern, value + _key + Colors.RESET, msg, count=1)

            record.msg = msg % arg_dict

        record.args = []

    @staticmethod
    def get_header_length(formatted_msg, record):
        """Get the header length of a given record."""
        if not isinstance(record.msg, dict):
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            _msg = ansi_escape.sub("", formatted_msg)
            try:
                _len = len(_msg) - len(record.msg % record.args)
            except:
                pass
            else:
                return _len
        return 0

    @staticmethod
    def is_serializable(msg):
        try:
            json.dumps(msg)
            return True
        except (TypeError, OverflowError):
            return False


class Format:
    SIMPLE = "%(asctime)s %(levelname)-8s %(module)s: %(message)s"
    VERBOSE = "%(asctime)s %(levelname)-8s %(filename)s:%(lineno)s:%(funcName)s: %(message)s"


class DateFormat:
    SIMPLE = "%H:%M:%S"
    VERBOSE = "%Y-%m-%d %H:%M:%S"


def get_logger_list():
    return [logging.getLogger(name) for name in logging.Logger.manager.loggerDict]


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "log"

os.makedirs(LOG_DIR, exist_ok=True)

# stream handler
stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_formatter = ColorizedFormatter(fmt=Format.SIMPLE, datefmt=DateFormat.SIMPLE)
stream_handler.setFormatter(stream_formatter)

# root logger
logging.basicConfig(
    level=logging.INFO,
    format=Format.SIMPLE,
    datefmt=DateFormat.SIMPLE,
    handlers=[stream_handler]
)


# flask logger
def init_logger(app):
    file_handler = RotatingFileHandler(
        filename=LOG_DIR / app.name,
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    app.logger.addHandler(stream_handler)
    app.logger.addHandler(file_handler)
    app.logger.propagate = False


# celery logger
@setup_logging.connect
def logger_setup_handler(*args, **kwargs):
    file_handler = RotatingFileHandler(
        filename=LOG_DIR / "celery.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    logger = logging.getLogger("celery")
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
