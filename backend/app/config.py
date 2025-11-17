"""Application configuration"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    ENVIRONMENT: str = Field(default="production")
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(...)

    # Database
    DATABASE_URL: str = Field(...)
    REDIS_URL: str = Field(...)

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(...)
    ADMIN_USER_ID: int = Field(...)

    # TON Blockchain
    RAFFLE_WALLET_ADDRESS: str = Field(...)
    RAFFLE_WALLET_MNEMONIC: str = Field(...)
    TON_CENTER_API_KEY: str = Field(...)

    # Random.org
    RANDOM_ORG_API_KEY: str = Field(...)

    # Raffle Configuration
    EXPRESS_MIN_PARTICIPANTS: int = Field(default=5)
    EXPRESS_ENTRY_FEE: float = Field(default=1.0)
    EXPRESS_TIMER_MINUTES: int = Field(default=1)

    STANDARD_MIN_PARTICIPANTS: int = Field(default=10)
    STANDARD_ENTRY_FEE: float = Field(default=2.0)
    STANDARD_TIMER_MINUTES: int = Field(default=2)

    PREMIUM_MIN_PARTICIPANTS: int = Field(default=30)
    PREMIUM_ENTRY_FEE: float = Field(default=5.0)
    PREMIUM_TIMER_MINUTES: int = Field(default=5)

    COMMISSION_PERCENT: float = Field(default=10.0)

    # CORS
    CORS_ORIGINS: str = Field(default="*")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
