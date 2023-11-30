import logging
import os
import time

import aiohttp
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

from src.modules import command_system
from src.modules.command_system import CommandType
from src.modules.vk_audio import recognize_audio_file

logger = logging.getLogger("global_logger")


async def _download_audio_message(audio_message_link: str) -> str:
    ts_start = time.perf_counter()
    logger.debug("downloading audio-message")
    async with aiohttp.ClientSession() as session:
        async with session.get(audio_message_link) as resp:
            data = await resp.content.read()
            filename = audio_message_link.split("/")[-1]
            temp_dir_name = "tmp"
            os.makedirs(temp_dir_name, exist_ok=True)
            file_path = os.path.join(temp_dir_name, filename)
            with open(file_path, "wb") as f:
                f.write(data)
    duration = time.perf_counter() - ts_start
    file_size = os.stat(file_path).st_size
    logger.debug(
        msg="downloading audio-message complete",
        extra={"duration": duration, "size_bytes": file_size},
    )
    return file_path


async def prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Отправьте голосовое сообщение для распознавания"
    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=context.bot_data["keyboards"]["cancel"],
    )
    return resp_message


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ts_start = time.perf_counter()
    logger.debug("start audio processing")
    logger.debug("start VK Audio processing")
    user_voice_id = update.message.voice.file_id
    user_voice = await context.bot.get_file(file_id=user_voice_id)
    user_voice_url = user_voice.file_path
    audio_file_path = await _download_audio_message(user_voice_url)

    try:
        resp_message_text = await recognize_audio_file(audio_file_path)
    except ClientConnectorError:
        resp_message_text = "[ошибка подключения к API VK, повторите попытку]"

    duration = time.perf_counter() - ts_start
    logger.debug(msg="end VK Audio processing", extra={"duration": duration})

    if resp_message_text == "":
        resp_message_text = "[тишина]"

    os.remove(audio_file_path)

    resp_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=resp_message_text)

    duration = time.perf_counter() - ts_start
    logger.debug(msg="end audio processing", extra={"duration": duration})
    return resp_message


command = command_system.Command(
    label="Распознавание речи от VK",
    command="command_audio_vk",
    command_type=CommandType.VOICE,
    description="Это команда переводит аудиосообщение в текст.",
    handler=command_handler,
    prompt_handler=prompt_handler,
)
