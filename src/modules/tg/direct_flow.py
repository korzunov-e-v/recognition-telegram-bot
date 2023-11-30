import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from src.modules.command_system import command_map
from src.utils import log_for_handler_decorator

logger = logging.getLogger("global_logger")


@log_for_handler_decorator
async def log_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_message = await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document="tg-bot.log",
        caption="Логи бота",
        filename="tg-bot.log",
    )
    return resp_message


@log_for_handler_decorator
async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_class = command_map.get("command_kaldi")
    resp_message = await command_class.process(update, context)
    return resp_message


@log_for_handler_decorator
async def photo_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_class = command_map.get("command_graphic_yolo")
    resp_message = await command_class.process(update, context)
    return resp_message


@log_for_handler_decorator
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте голосовое сообщение для распознавания речи или изображение для распознавания объектов",
        reply_markup=ReplyKeyboardRemove(),
    )
    return resp_message


@log_for_handler_decorator
async def sticker_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Классный стикер =). Но я их не распознаю",
        reply_markup=ReplyKeyboardRemove(),
    )
    return resp_message


@log_for_handler_decorator
async def other_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сообщение не распознано",
        reply_markup=ReplyKeyboardRemove(),
    )
    return resp_message
