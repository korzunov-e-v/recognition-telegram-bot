import re

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.config import service_settings
from src.modules.command_system import get_all_keyboards
from src.modules.tg import button_flow, direct_flow


def get_application(bot_access_token: str) -> Application:
    application = ApplicationBuilder().token(bot_access_token).build()

    if service_settings.flow == "direct":
        log_command_handler = CommandHandler("logs", direct_flow.log_command_handler)
        voice_handler = MessageHandler(filters.VOICE, direct_flow.voice_message_handler)
        photo_handler = MessageHandler(filters.PHOTO, direct_flow.photo_message_handler)
        text_handler = MessageHandler(filters.TEXT, direct_flow.text_message_handler)
        sticker_handler = MessageHandler(filters.Sticker.ALL, direct_flow.sticker_message_handler)
        other_handler = MessageHandler(filters.ALL, direct_flow.other_message_handler)

        application.add_handlers(
            [
                log_command_handler,
                voice_handler,
                photo_handler,
                text_handler,
                sticker_handler,
                other_handler,
            ]
        )
    elif service_settings.flow == "button":
        keyboards = get_all_keyboards()
        application.bot_data["keyboards"] = keyboards

        log_command_handler = CommandHandler("logs", direct_flow.log_command_handler)
        info_command_handler = CommandHandler("info", button_flow.info_command_handler)
        start_handler = CommandHandler("start", button_flow.start_conversation_handler)
        cancel_handler = MessageHandler(
            filters.Regex(re.compile("^Отмена$", re.IGNORECASE)), button_flow.start_conversation_handler
        )
        message_filter = (
            filters.VOICE | filters.PHOTO | filters.TEXT | filters.VIDEO_NOTE | filters.Document.ALL | filters.LOCATION
        )
        message_handler = MessageHandler(message_filter, button_flow.message_handler)
        sticker_handler = MessageHandler(filters.Sticker.ALL, direct_flow.sticker_message_handler)
        other_handler = MessageHandler(filters.ALL, direct_flow.other_message_handler)

        application.add_handlers(
            [
                log_command_handler,
                info_command_handler,
                start_handler,
                cancel_handler,
                message_handler,
                sticker_handler,
                other_handler,
            ]
        )
    else:
        raise

    return application
