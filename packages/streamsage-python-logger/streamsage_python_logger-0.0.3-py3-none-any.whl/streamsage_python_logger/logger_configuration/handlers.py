from streamsage_python_logger.settings.settings import LoggerSettings

logger_config = LoggerSettings()

handlers = {
    "default": {
        "formatter": "default",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stderr",
        "level": logger_config.LOG_SDK_TRANSPORT_CONSOLE_LEVEL
    },
    "fluent": {
        "host": logger_config.LOG_SDK_TRANSPORT_FLUENT_URL.split(':')[0],
        "port": int(logger_config.LOG_SDK_TRANSPORT_FLUENT_URL.split(':')[1]),
        "tag": "logging",
        "buffer_overflow_handler": "overflow_handler",
        "formatter": "default",
        "timeout": logger_config.LOG_SDK_TRANSPORT_FLUENT_TIMEOUT,
        "level": logger_config.LOG_SDK_TRANSPORT_FLUENT_LEVEL,
        "class": "fluent.asynchandler.FluentHandler",
    },
}
