from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    scibox_api_key: str
    willow_server_url: str = "http://localhost:8001"  # URL Willow Inference Server
    willow_api_key: str = ""  # API ключ для Willow (если требуется)

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорируем дополнительные поля из переменных окружения
    )


settings = Settings()
