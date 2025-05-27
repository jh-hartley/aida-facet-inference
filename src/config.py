import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator

load_dotenv()


class Config:
    BASE_DIR: Path = Path(__file__).parent.absolute()

    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_LLM_TEMPERATURE: float = float(os.getenv("OPENAI_LLM_TEMPERATURE", "0.7"))
    OPENAI_LLM_TOP_P: float = float(os.getenv("OPENAI_LLM_TOP_P", "1.0"))
    OPENAI_LLM_FREQ_PENALTY: float = float(os.getenv("OPENAI_LLM_FREQ_PENALTY", "0.0"))
    OPENAI_LLM_REASONING_EFFORT: str = os.getenv("OPENAI_LLM_REASONING_EFFORT", "medium")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "aida_db")
    DB_USER: str = os.getenv("DB_USER", "aida_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_USE_SSL: bool = os.getenv("DB_USE_SSL", "False").lower() == "true"

    # Database Pool Configuration
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    DB_ASYNC_POOL_SIZE: int = int(os.getenv("DB_ASYNC_POOL_SIZE", "20"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, value: str) -> str:
        if not value:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value not in valid_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL: {value}. Must be one of {valid_levels}"
            )
        return value

    @field_validator("DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_ASYNC_POOL_SIZE")
    @classmethod
    def validate_pool_size(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Pool size must be at least 1")
        return value

    @field_validator("OPENAI_LLM_TEMPERATURE", "OPENAI_LLM_TOP_P", "OPENAI_LLM_FREQ_PENALTY")
    @classmethod
    def validate_float_range(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("Value must be between 0 and 1")
        return value

    @field_validator("OPENAI_LLM_REASONING_EFFORT")
    @classmethod
    def validate_reasoning_effort(cls, value: str) -> str:
        valid_efforts = ["low", "medium", "high"]
        if value.lower() not in valid_efforts:
            raise ValueError(f"Invalid reasoning effort: {value}. Must be one of {valid_efforts}")
        return value.lower()


config = Config()