import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationInfo, field_validator

load_dotenv()


class Config:
    BASE_DIR: Path = Path(__file__).parent.absolute()

    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    OPENAI_LLM_TEMPERATURE: float = float(
        os.getenv("OPENAI_LLM_TEMPERATURE", "0.0")
    )
    OPENAI_LLM_TOP_P: float = float(os.getenv("OPENAI_LLM_TOP_P", "0.1"))
    OPENAI_LLM_FREQ_PENALTY: float = float(
        os.getenv("OPENAI_LLM_FREQ_PENALTY", "0.1")
    )
    OPENAI_LLM_REASONING_EFFORT: str = os.getenv(
        "OPENAI_LLM_REASONING_EFFORT", "high"
    )

    # Embedding Configuration
    EMBEDDING_MIN_DIMENSIONS: int = int(
        os.getenv("EMBEDDING_MIN_DIMENSIONS", "1536")
    )
    EMBEDDING_MAX_DIMENSIONS: int = int(
        os.getenv("EMBEDDING_MAX_DIMENSIONS", "1536")
    )
    EMBEDDING_DEFAULT_DIMENSIONS: int = int(
        os.getenv("EMBEDDING_DEFAULT_DIMENSIONS", "1536")
    )

    # Similarity Search Configuration
    SIMILARITY_DEFAULT_LIMIT: int = int(
        os.getenv("SIMILARITY_DEFAULT_LIMIT", "10")
    )
    SIMILARITY_MAX_LIMIT: int = int(os.getenv("SIMILARITY_MAX_LIMIT", "50"))
    SIMILARITY_MIN_DISTANCE: float = float(
        os.getenv("SIMILARITY_MIN_DISTANCE", "0.0")
    )
    SIMILARITY_MAX_DISTANCE: float = float(
        os.getenv("SIMILARITY_MAX_DISTANCE", "2.0")
    )
    SIMILARITY_DEFAULT_DISTANCE: float = float(
        os.getenv("SIMILARITY_DEFAULT_DISTANCE", "0.6")
    )

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

    # Embedding Backoff/Retry Configuration
    OPENAI_EMBEDDING_MAX_TRIES: int = int(
        os.getenv("OPENAI_EMBEDDING_MAX_TRIES", "5")
    )
    OPENAI_EMBEDDING_MAX_TIME: int = int(
        os.getenv("OPENAI_EMBEDDING_MAX_TIME", "60")
    )

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

    @field_validator(
        "OPENAI_LLM_TEMPERATURE", "OPENAI_LLM_TOP_P", "OPENAI_LLM_FREQ_PENALTY"
    )
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
            raise ValueError(
                f"Invalid reasoning effort: {value}. "
                f"Must be one of {valid_efforts}"
            )
        return value.lower()

    @field_validator(
        "EMBEDDING_MIN_DIMENSIONS",
        "EMBEDDING_MAX_DIMENSIONS",
        "EMBEDDING_DEFAULT_DIMENSIONS",
    )
    @classmethod
    def validate_embedding_dimensions(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Embedding dimensions must be at least 1")
        return value

    @field_validator("EMBEDDING_DEFAULT_DIMENSIONS")
    @classmethod
    def validate_default_dimensions(
        cls, value: int, info: ValidationInfo
    ) -> int:
        min_dims = info.data.get("EMBEDDING_MIN_DIMENSIONS", 384)
        max_dims = info.data.get("EMBEDDING_MAX_DIMENSIONS", 4096)
        if not min_dims <= value <= max_dims:
            raise ValueError(
                f"Default dimensions must be between min ({min_dims}) "
                f"and max ({max_dims}) dimensions"
            )
        return value

    @field_validator("SIMILARITY_DEFAULT_LIMIT", "SIMILARITY_MAX_LIMIT")
    @classmethod
    def validate_similarity_limit(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Similarity limit must be at least 1")
        return value

    @field_validator("SIMILARITY_DEFAULT_LIMIT")
    @classmethod
    def validate_default_limit(cls, value: int, info: ValidationInfo) -> int:
        max_limit = info.data.get("SIMILARITY_MAX_LIMIT", 50)
        if value > max_limit:
            raise ValueError(
                f"Default limit must not exceed max limit ({max_limit})"
            )
        return value

    @field_validator(
        "SIMILARITY_MIN_DISTANCE",
        "SIMILARITY_MAX_DISTANCE",
        "SIMILARITY_DEFAULT_DISTANCE",
    )
    @classmethod
    def validate_similarity_distance(cls, value: float) -> float:
        if not 0 <= value <= 2:
            raise ValueError("Cosine distance must be between 0 and 2")
        return value

    @field_validator("SIMILARITY_DEFAULT_DISTANCE")
    @classmethod
    def validate_default_distance(
        cls, value: float, info: ValidationInfo
    ) -> float:
        min_distance = info.data.get("SIMILARITY_MIN_DISTANCE", 0.0)
        max_distance = info.data.get("SIMILARITY_MAX_DISTANCE", 2.0)
        if not min_distance <= value <= max_distance:
            raise ValueError(
                f"Default distance must be between min ({min_distance}) "
                f"and max ({max_distance}) distance"
            )
        return value


config = Config()
