from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # Existing settings...
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FakeCatcher++"

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_RESUME_EXTENSIONS: List[str] = Field(default_factory=lambda: [".pdf", ".doc", ".docx"])

    # NEW: Hugging Face AI Settings
    HUGGINGFACE_API_KEY: str = Field(default="")
    HF_API_URL: str = "https://api-inference.huggingface.co/models"
    AI_DETECTION_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("AI_DETECTION_ENABLED", "true").lower() == "true")
    AI_CACHE_ENABLED: bool = Field(default_factory=lambda: os.getenv("AI_CACHE_ENABLED", "true").lower() == "true")
    AI_CACHE_DURATION: int = 3600

    # AI Model Configuration
    HF_AI_DETECTOR_MODEL: str = "Hello-SimpleAI/chatgpt-detector-roberta"
    HF_TEXT_CLASSIFIER_MODEL: str = "microsoft/DialoGPT-medium"
    HF_CONTENT_ANALYZER_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    # AI Detection Parameters
    AI_CONFIDENCE_THRESHOLD: float = 0.75
    AI_ENSEMBLE_WEIGHT: float = 0.7
    RULE_BASED_WEIGHT: float = 0.3
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 30

    # Trust Score Weights (existing)
    RESUME_WEIGHT: float = 0.3
    VIDEO_WEIGHT: float = 0.4
    AUDIO_WEIGHT: float = 0.3

    # Development
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
