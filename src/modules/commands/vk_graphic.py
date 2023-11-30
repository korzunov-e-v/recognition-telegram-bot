import logging
import os
import time

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from src.modules import command_system
from src.modules.command_system import CommandType
from src.modules.vk_graphic import recognize_image

logger = logging.getLogger("global_logger")


async def _download_photo(photo_url):
    ts_start = time.perf_counter()
    logger.debug("downloading photo")
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as resp:
            data = await resp.content.read()
            filename = photo_url.split("/")[-1]
            temp_dir_name = "tmp"
            os.makedirs(temp_dir_name, exist_ok=True)
            file_path = os.path.join(temp_dir_name, filename)
            with open(file_path, "wb") as f:
                f.write(data)
    duration = time.perf_counter() - ts_start
    file_size = os.stat(file_path).st_size
    logger.debug(
        msg="downloading photo complete",
        extra={"duration": duration, "size_bytes": file_size},
    )
    return file_path


async def prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Отправьте изображения для распознавания"
    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=context.bot_data["keyboards"]["cancel"],
    )
    return resp_message


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ts_start = time.perf_counter()
    logger.debug("start image processing")

    photo_id = update.message.photo[-1].file_id
    request_photo = await context.bot.get_file(file_id=photo_id)
    request_photo_url = request_photo.file_path
    photo_path = await _download_photo(request_photo_url)
    try:
        result = await recognize_image(photo_path)
    except BaseException as e:
        resp_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сервис VK Vision недоступен",
        )
        logger.error(
            msg="vk vision unavailable",
            extra={"exception": {"status": e.code, "message": e.message, "request_info": e.request_info}},
        )
        duration = time.perf_counter() - ts_start
        logger.debug(msg="end image processing", extra={"duration": duration})
        return resp_message

    resp_message_text = ""
    resp_message_text += "Изображение:\n"
    recognized_objects = result["object_labels"]
    if len(recognized_objects) == 0 or recognized_objects[0].get("labels") is None:
        resp_message_text += "[Объекты не распознаны]\n"
    else:
        for obj in recognized_objects[0]["labels"]:
            obj_name = obj["rus"]
            probability = obj["prob"] * 100
            obj_result = f"{probability:.2f}% - {obj_name}"
            if obj["rus_categories"]:
                obj_result += f" {obj['rus_categories']}"
            obj_result += "\n"
            resp_message_text += obj_result
        resp_message_text += "\n"

    resp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=resp_message_text,
    )

    duration = time.perf_counter() - ts_start
    logger.debug(msg="end image processing", extra={"duration": duration})
    return resp_message


command = command_system.Command(
    label="Распознавание изображений Mail Vision",
    command="command_graphic_vk",
    command_type=CommandType.PHOTO,
    description="Это команда распознаёт объекты на изображении.",
    handler=command_handler,
    prompt_handler=prompt_handler,
)
