import logging
from contextlib import suppress

from telegram import Update
from telegram.ext import ContextTypes

from src.modules.command_system import command_map, label_map
from src.utils import get_message_type, log_for_handler_decorator

logger = logging.getLogger("global_logger")


@log_for_handler_decorator
async def info_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = command_map.get("info")
    resp_message = await command.send_prompt(update, context)
    return resp_message


@log_for_handler_decorator
async def start_conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = " ".join(context.args) if context.args else None
    if not arg:
        resp_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите команду на клавиатуре",
            reply_markup=context.bot_data["keyboards"]["main"],
        )
        with suppress(KeyError):
            del context.user_data["command"]
        return resp_message

    command = label_map.get(arg)
    context.user_data["command"] = command.command
    resp_message = await command.send_prompt(update, context)
    return resp_message


@log_for_handler_decorator
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = context.user_data.get("command")
    if not command:
        resp_message_text = "Вы не выбрали команду на клавиатуре"
        resp_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=resp_message_text,
            reply_markup=context.bot_data["keyboards"]["main"],
        )
        return resp_message

    message_type = get_message_type(update)
    command_class = command_map.get(command)
    if command_class.command_type != message_type:
        resp_message_text = (
            f"Сообщение типа '{message_type.repr_name}' не ожидалось. \n"
            f"Пришлите {command_class.command_type.repr_name} или нажмите Отмена для возврата в главное меню."
        )
        resp_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=resp_message_text)
        return resp_message

    resp_message = await command_class.process(update, context)
    return resp_message
