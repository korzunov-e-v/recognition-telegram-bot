import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    flow: str = Field(
        "button",
        description="Режим работы ('direct'/'button'), используется модуль direct_flow или button_flow.",
    )

    app_name: str = "korzunov-e-v-tg-bot"
    log_level: int = Field(logging.INFO, description="Уровень логирования")
    bot_token: str = Field(description="Токен бота в Телеграм")

    vk_api_token: str = Field(description="Сервисный ключ приложения Вконтакте")
    vision_api_token: str = Field(description="Сервисный токен для Vision")


service_settings = ServiceSettings()
