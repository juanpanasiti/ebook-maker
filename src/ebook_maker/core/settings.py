from pathlib import Path

from pydantic import DirectoryPath, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_ENV = str(Path.home() / ".config" / "ebook-maker" / ".env")


class Settings(BaseSettings):
    obsidian_root: DirectoryPath
    epub_destination: Path
    default_author: str = "Unknown Author"
    default_publisher: str | None = None
    
    # Email settings for Send to Kindle
    kindle_email: str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

    model_config = SettingsConfigDict(env_file=(CONFIG_ENV, ".env"), env_file_encoding="utf-8", extra="ignore")

    @field_validator("epub_destination", mode="after")
    @classmethod
    def ensure_epub_dest_exists(cls, v: Path) -> Path:
        """Ensure the output directory exists, creating it if necessary."""
        v.mkdir(parents=True, exist_ok=True)
        return v


def get_settings() -> Settings:
    """Load and return the application settings."""
    return Settings()
