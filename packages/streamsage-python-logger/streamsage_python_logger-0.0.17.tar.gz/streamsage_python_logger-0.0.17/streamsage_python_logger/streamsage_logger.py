import logging
from logging.config import dictConfig

from pydantic import BaseSettings, validator

from streamsage_python_logger.settings.settings import LoggerSettings
from streamsage_python_logger.logger_configuration.formatters import formatters
from streamsage_python_logger.logger_configuration.handlers import handlers


class LoggerConfig(BaseSettings):
    context: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    logger_config = LoggerSettings()
    LOG_LEVEL: str = logger_config.LOG_SDK_TRANSPORT_FLUENT_LEVEL

    version = 1
    disable_existing_loggers = False

    formatters = formatters
    handlers = handlers
    loggers = {
        context: {"handlers": logger_config.LOG_SDK_TRANSPORTS.split(","), "level": LOG_LEVEL},
    }

    class Config:
        validate_assignment = True

    @validator('context')
    def set_name(cls, context):
        return context


def get_logger(context):
    dictConfig(LoggerConfig(context=context).dict())
    return logging.getLogger(context)
