import logging
import sys
from logging.handlers import RotatingFileHandler

from backend.app.config import settings


def setup_logging() -> None:
    logger = logging.getLogger("agnes")
    logger.setLevel(settings.log_level.upper())

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        "agnes.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    logger.info("Logging initialized (level=%s)", settings.log_level)
