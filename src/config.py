"""Core configuration and settings for the Agentic CI/CD Engineer."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GOOGLE = "google"
    LOCAL = "local"


class CICDPlatform(str, Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"
    AZURE_DEVOPS = "azure_devops"


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITALOCEAN = "digitalocean"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CICD_AGENT_",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "Agentic CI/CD Engineer"
    debug: bool = False
    log_level: str = "INFO"

    # --- LLM Configuration ---
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_model: str = "gpt-4o"
    llm_fallback_model: str = "claude-3-5-sonnet-20241022"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 8192
    llm_token_budget_per_run: int = 100_000  # Max tokens per pipeline generation run

    # --- API Keys ---
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    groq_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None  # Google AI Studio / Gemini
    github_token: Optional[SecretStr] = None
    gitlab_token: Optional[SecretStr] = None

    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cicd_agent"
    redis_url: str = "redis://localhost:6379/0"

    # --- Vector Store ---
    vector_store_type: str = "chromadb"
    chromadb_persist_dir: str = "./data/chromadb"

    # --- Sandbox ---
    sandbox_enabled: bool = True
    sandbox_timeout_seconds: int = 300
    sandbox_max_memory_mb: int = 2048
    docker_socket: str = "unix:///var/run/docker.sock"

    # --- Pipeline Generation ---
    max_self_healing_retries: int = 3
    default_cicd_platform: CICDPlatform = CICDPlatform.GITHUB_ACTIONS
    require_human_approval: bool = True

    # --- Paths ---
    templates_dir: Path = Path("src/templates")
    knowledge_base_dir: Path = Path("data/knowledge_base")
    artifacts_dir: Path = Path("data/artifacts")

    # --- API Server ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000


# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
