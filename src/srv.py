import logging
import sys

import logging_loki

from src.config import service_settings
from src.modules.command_system import load_modules
from src.modules.tg.tg import get_application
from src.utils import CustomJSONFormatter

logger = logging.getLogger("global_logger")
logger.setLevel(service_settings.log_level)

file_handler = logging.FileHandler(filename="tg-bot.log", encoding="utf-8")
stdout_handler = logging.StreamHandler(stream=sys.stdout)

json_formatter = CustomJSONFormatter()

file_handler.setFormatter(json_formatter)
stdout_handler.setFormatter(json_formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


if __name__ == "__main__":
    load_modules()
    application = get_application(service_settings.bot_token)
    logger.info("polling started")
    application.run_polling()
