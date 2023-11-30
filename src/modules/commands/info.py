from telegram import Update
from telegram.ext import ContextTypes

from src.modules import command_system
from src.modules.command_system import CommandType


async def prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ""
    command_list = list(command_system.command_map.keys())
    command_list.remove("info")
    for command_name in command_list:
        command = command_system.command_map[command_name]
        message += command.label + " - " + command.description + "\n\n"
    keyboard = context.bot_data["keyboards"]["main"]
    resp_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=keyboard)
    return resp_message


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


info_command = command_system.Command(
    label="Информация о командах",
    command="info",
    command_type=CommandType.TEXT,
    description="Выводит список команд и их описания.",
    handler=command_handler,
    prompt_handler=prompt_handler,
)
