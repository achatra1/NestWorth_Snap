from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from pathlib import Path

# Get the directory where this config.py file is located
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_ENV: str = "development"
    PORT: int = 8000
    
    # MongoDB
    MONGODB_URI: str
    
    # JWT
    JWT_SECRET: str
    JWT_EXPIRES_IN: int = 86400  # 24 hours in seconds
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # OpenAI
    OPENAI_API_KEY: str = ""

    # Resend (transactional email)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "NestWorth <onboarding@resend.dev>"

    # Frontend base URL (used to build links embedded in emails, e.g. password reset)
    FRONTEND_URL: str = "http://localhost:5137"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()