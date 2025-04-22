import importlib
import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    PROJECT_NAME: str = "FAAC Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    # SECURITY
    SECRET_KEY: str = "change_this_in_production"

    # API keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    IDEOGRAM_API_KEY: str = os.getenv("IDEOGRAM_API_KEY")
    ELEVEN_LABS_API_KEY: str = os.getenv("ELEVEN_LABS_API_KEY")
    OPEN_SYMBOLS_SECRET_KEY: str = os.getenv("OPEN_SYMBOLS_SECRET_KEY")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY")

    # Digital Ocean
    SPACES_KEY: str = os.getenv("SPACES_KEY")
    SPACES_SECRET: str = os.getenv("SPACES_SECRET")
    BUCKET: str = os.getenv("BUCKET")
    REGION: str = os.getenv("REGION")

    # Database
    DATABASE_URL: str = "sqlite:///./faac.db"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # File storage
    # UPLOAD_DIR: Path = Path("uploads")
    # PICTURES_DIR: Path = UPLOAD_DIR / "pictures"
    # AUDIO_DIR: Path = UPLOAD_DIR / "audio"

    def reload_settings(self) -> None:
        """
        Reload settings from environment variables.

        This method reloads environment variables and updates the settings
        object with any new values, useful after .env file changes.
        """
        # Force reload environment variables
        importlib.reload(os)

        self.ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", self.ADMIN_API_KEY)


settings = Settings()

# Ensure upload directories exist
# os.makedirs(settings.PICTURES_DIR, exist_ok=True)
# os.makedirs(settings.AUDIO_DIR, exist_ok=True)
