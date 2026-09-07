import logging.config
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

LOG_FILE_PATH = PROJECT_ROOT / os.getenv("LOG_FILE_PATH", "logs/app.log")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console_format": {
            "format": "%(levelname)s - %(name)s - %(message)s",
        },
        "file_format": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console_format",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "file_format",
            "filename": str(LOG_FILE_PATH),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)