import enum
import importlib
import os
from typing import Callable

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes


class CommandType(enum.Enum):
    TEXT = "text", "текстовое сообщение"
    VOICE = "voice", "голосовое сообщение"
    PHOTO = "photo", "изображение"
    VIDEO = "video", "видеозапись"
    STICKER = "sticker", "стикер"
    VIDEO_NOTE = "video_note", "кружочек"
    DOCUMENT = "document", "документ"
    OTHER = "other", "другое"

    def __new__(cls, value, repr_name):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.repr_name = repr_name
        return obj


class Command:
    def __init__(
        self,
        label: str,
        command: str,
        command_type: CommandType,
        description: str,
        handler: Callable,
        prompt_handler: Callable,
    ):
        self.label = label
        self.command = command
        self.command_type = command_type
        self.description = description
        self.handler = handler
        self.prompt_handler = prompt_handler
        command_map[command] = self
        label_map[label] = self

    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.handler(update, context)

    async def send_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.prompt_handler(update, context)


def get_all_keyboards() -> dict[str, ReplyKeyboardMarkup]:
    keyboards = {}

    kb_cancel = [["Отмена"]]
    kbm_cancel = ReplyKeyboardMarkup(keyboard=kb_cancel, resize_keyboard=True)
    keyboards["cancel"] = kbm_cancel

    commands_keys = list(command_map.keys())
    commands_keys.remove("info")
    sorted_commands_keys = sorted(commands_keys)
    kb_main = []
    for command_key in sorted_commands_keys:
        command = command_map[command_key]
        kb_main.append([f"/start {command.label}"])
    kb_main.append(["/info Информация о командах"])
    kbm_main = ReplyKeyboardMarkup(keyboard=kb_main, resize_keyboard=True)
    keyboards["main"] = kbm_main

    return keyboards


command_map: dict[str, Command] = {}
label_map: dict[str, Command] = {}


def load_modules() -> None:
    files = os.listdir("src/modules/commands")
    modules = filter(lambda x: x.endswith(".py"), files)
    for m in modules:
        importlib.import_module("src.modules.commands." + m[0:-3])
