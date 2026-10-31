import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=True)

class Settings(BaseSettings):
    """Runtime configuration parsed from environment variables and .env files."""
    APP_NAME: str = "Project Brain"
    DATABASE_URL: str = "sqlite:///./project_brain.db"
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "").strip()
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    BACKEND_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()