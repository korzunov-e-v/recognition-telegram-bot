import functools
import logging
import time
from datetime import datetime

from json_log_formatter import JSONFormatter, _json_serializable
from telegram import Message, Update
from telegram.ext import filters

from src.modules.command_system import CommandType


class CustomJSONFormatter(JSONFormatter):
    def to_json(self, record):
        try:
            return self.json_lib.dumps(record, ensure_ascii=False, default=_json_serializable)
        except (TypeError, ValueError, OverflowError):
            try:
                return self.json_lib.dumps(record)
            except (TypeError, ValueError, OverflowError):
                return "{}"

    def json_record(self, message, extra, record):
        result = {}
        if "time" not in extra:
            result["time"] = datetime.utcnow()

        result["levelname"] = record.levelname
        result["message"] = message
        result.update(extra)

        if record.exc_info:
            result["exc_info"] = self.formatException(record.exc_info)

        return result


def get_message_att_info(message: Message):
    if isinstance(message.effective_attachment, tuple):
        attachments_type = type(message.effective_attachment[-1]).__name__
        attachment = message.effective_attachment[-1].to_dict()
    else:
        attachments_type = type(message.effective_attachment).__name__ if message.effective_attachment else None
        attachment = message.effective_attachment.to_dict() if message.effective_attachment else None
    return attachments_type, attachment


def get_message_type(update: Update):
    if filters.VIDEO.check_update(update):
        return CommandType.VIDEO
    elif filters.VOICE.check_update(update):
        return CommandType.VOICE
    elif filters.PHOTO.check_update(update):
        return CommandType.PHOTO
    elif filters.Sticker.ALL.check_update(update):
        return CommandType.STICKER
    elif filters.TEXT.check_update(update):
        return CommandType.TEXT
    elif filters.VIDEO_NOTE.check_update(update):
        return CommandType.VIDEO_NOTE
    elif filters.Document.ALL.check_update(update):
        return CommandType.DOCUMENT
    else:
        return CommandType.OTHER


def log_for_handler_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ts_start = time.perf_counter()
        logger = logging.getLogger("global_logger")
        update = args[0]

        resp_message = await func(*args, **kwargs)
        duration = time.perf_counter() - ts_start
        req_attachments_type, req_attachments = get_message_att_info(update.message)
        resp_attachments_type, resp_attachments = get_message_att_info(resp_message)
        logger.info(
            msg="Message sent",
            extra={
                "req_chat_id": update.effective_chat.id,
                "req_user_id": update.effective_user.id,
                "req_user_username": update.effective_user.username,
                "req_message": update.message.text,
                "req_attachments_type": req_attachments_type,
                "req_attachments": req_attachments,
                "resp_message": resp_message.text or resp_message.caption,
                "resp_attachments_type": resp_attachments_type,
                "resp_attachments": resp_attachments,
                "resp_time": duration,
            },
        )
        return resp_message

    return wrapper
