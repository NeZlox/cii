import logging
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger

from src.config import settings

logging.captureWarnings(True)

"""
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.INFO
        )
"""

logger = logging.getLogger()

# куда пишем лог
logHandler = logging.StreamHandler()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Добавление поля msg
        log_record["msg"] = record.getMessage()


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(status)s %(module)s %(funcName)s"
)

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(settings.LOG_LEVEL)
