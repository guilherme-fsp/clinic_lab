from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()

class Settings(BaseSettings):
    GEMINI_OCR_MODEL: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding="utf-8"
        case_sensitive=True
        extra="allow"

def settings_config() -> Settings:
    return Settings()