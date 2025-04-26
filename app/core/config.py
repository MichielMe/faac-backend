import importlib
import json
import os
from typing import List, Union

from pydantic import field_validator
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

    # Database - Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        """
        Parse BACKEND_CORS_ORIGINS from environment as JSON list or comma-separated string.
        """
        if isinstance(v, str):
            # Fallback parsing: comma-separated or JSON-like
            try:
                return json.loads(v)
            except ValueError:
                if v.startswith("[") and v.endswith("]"):
                    inner = v[1:-1]
                else:
                    inner = v
                return [
                    item.strip().strip('"').strip("'")
                    for item in inner.split(",")
                    if item.strip()
                ]
        return v

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
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", self.SUPABASE_URL)
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", self.SUPABASE_KEY)


settings = Settings()

# Ensure upload directories exist
# os.makedirs(settings.PICTURES_DIR, exist_ok=True)
# os.makedirs(settings.AUDIO_DIR, exist_ok=True)
