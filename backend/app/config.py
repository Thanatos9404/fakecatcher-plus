from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FakeCatcher++"

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_RESUME_EXTENSIONS: List[str] = Field(default_factory=lambda: [".pdf", ".doc", ".docx"])
    ALLOWED_VIDEO_EXTENSIONS: List[str] = Field(default_factory=lambda: [".mp4", ".avi", ".mov"])
    ALLOWED_AUDIO_EXTENSIONS: List[str] = Field(default_factory=lambda: [".mp3", ".wav", ".m4a"])

    # AI Model Settings
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    DEEPFAKE_THRESHOLD: float = 0.8
    VOICE_CLONE_THRESHOLD: float = 0.75

    # Trust Score Weights
    RESUME_WEIGHT: float = 0.3
    VIDEO_WEIGHT: float = 0.4
    AUDIO_WEIGHT: float = 0.3

    # Development
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
