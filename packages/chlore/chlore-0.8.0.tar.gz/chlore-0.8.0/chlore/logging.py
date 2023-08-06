import logging.config

import structlog

from .config import LoggingConfig
from .request import get_request


def request_logger() -> structlog.stdlib.BoundLogger:
    """
    Retrieve the logger associated with the current request
    """
    return structlog.get_logger().bind(request_id=get_request().state.id)


def get_standard_logging_config(config: LoggingConfig):
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": processors,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
                "foreign_pre_chain": processors,
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": config.format,
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "INFO",
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "pika": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    return logging_config


def setup_standard_logging(config: LoggingConfig):
    logging.config.dictConfig(get_standard_logging_config(config))


def setup_app_logging(config: LoggingConfig):
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="ISO"),
    ]

    if config.format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:  # config.format == "text"
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(processors=processors)
