from datetime import datetime
import logging
from logging import Formatter, Logger, StreamHandler
from typing import ClassVar, Self

import pytz


class ColorCode:
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[32;20m"
    CYAN = "\x1b[36;20m"
    MAGENTA = "\x1b[35;20m"
    RESET = "\x1b[0m"


class TimeColorFormatter(Formatter):
    COLORS: ClassVar = {
        logging.DEBUG: ColorCode.GREY,
        logging.INFO: ColorCode.GREEN,
        logging.WARNING: ColorCode.YELLOW,
        logging.ERROR: ColorCode.RED,
        logging.CRITICAL: ColorCode.BOLD_RED,
    }

    def __init__(self: Self, fmt: str) -> None:
        super().__init__()
        self.fmt: str = fmt

    def format_time(self: Self, record: logging.LogRecord, format_tz: str = "Asia/Bangkok") -> str:
        thai_tz = pytz.timezone(format_tz)
        thai_time = datetime.fromtimestamp(record.created, thai_tz)

        formatted_time = f"{thai_time.strftime('%a')} {thai_time.day}-{thai_time.month}-{thai_time.year} {thai_time.strftime('%H:%M:%S')}"
        return f"{ColorCode.CYAN}{formatted_time}{ColorCode.RESET}"

    def format(self: Self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelno, ColorCode.GREY)
        colored_time = self.format_time(record)

        return f"{colored_time} - {level_color}{record.levelname:8}{ColorCode.RESET} - {record.getMessage()}"


class LoggerConfig:
    def __init__(self: Self, name: str = "") -> None:
        self._logger: Logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        self._setup_handlers()

    def _setup_handlers(self: Self) -> None:
        formatter = TimeColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def info(self: Self, message: str) -> None:
        self._logger.info(message)

    def error(self: Self, message: str) -> None:
        self._logger.error(message)

    def warning(self: Self, message: str) -> None:
        self._logger.warning(message)

    def debug(self: Self, message: str) -> None:
        self._logger.debug(message)

    def critical(self: Self, message: str) -> None:
        self._logger.critical(message)

    @property
    def logger(self: Self) -> Logger:
        return self._logger


logger: Logger = LoggerConfig().logger
