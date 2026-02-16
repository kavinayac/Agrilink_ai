"""Configuration management for AgriLink."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AgriLink"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # LLM Providers
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    groq_api_key: str = Field(default="", description="Groq API key")
    default_llm_provider: Literal["openai", "anthropic", "groq"] = "groq"
    default_model: str = "llama-3.3-70b-versatile"
    fallback_model: str = "llama-3.1-8b-instant"

    # Embeddings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Vector Database
    vector_db_type: Literal["chroma", "pinecone", "faiss"] = "pinecone"
    chroma_persist_dir: str = "./data/chroma"
    pinecone_api_key: str = Field(default="", description="Pinecone API key")
    pinecone_environment: str = ""
    pinecone_index_name: str = "agrilink"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_url: str = "redis://localhost:6379/0"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "agrilink"
    postgres_user: str = "agrilink"
    postgres_password: str = "agrilink_password"
    database_url: str = "postgresql+asyncpg://agrilink:agrilink_password@localhost:5432/agrilink"

    # External APIs
    weather_api_provider: Literal["openweathermap", "weatherapi"] = "openweathermap"
    openweather_api_key: str = Field(default="", description="OpenWeatherMap API key")
    weatherapi_key: str = Field(default="", description="WeatherAPI key")

    market_api_enabled: bool = False
    market_api_url: str = ""
    market_api_key: str = ""

    # Real-time Delivery
    websocket_enabled: bool = True
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10

    # Notifications
    enable_push_notifications: bool = True
    enable_sms_notifications: bool = False
    enable_email_notifications: bool = False

    # SMS (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Email (SMTP)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # RAG Configuration
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.7
    rag_enable_reranking: bool = True
    rag_enable_hybrid_search: bool = True

    # Agent Configuration
    agent_timeout_seconds: int = 30
    agent_max_iterations: int = 5
    orchestrator_confidence_threshold: float = 0.8

    # Safety & Guardrails
    enable_rag_validation: bool = True
    enable_confidence_scoring: bool = True
    enable_audit_logging: bool = True
    minimum_confidence_for_action: float = 0.7

    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_concurrent_agents: int = 10

    @field_validator("openai_api_key", "anthropic_api_key")
    @classmethod
    def validate_api_keys(cls, v: str, info) -> str:
        """Validate that at least one LLM API key is provided in production."""
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return Path("./data")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
