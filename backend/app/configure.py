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
    ALLOWED_VIDEO_EXTENSIONS: List[str] = Field(default_factory=lambda: [".mp4", ".avi", ".mov", ".mkv"])
    ALLOWED_AUDIO_EXTENSIONS: List[str] = Field(default_factory=lambda: [".mp3", ".wav", ".m4a", ".flac"])

    # NEW: Job Posting File Types (includes images)
    ALLOWED_JOB_POSTING_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp"])

    # AI Model Settings
    AI_CONFIDENCE_THRESHOLD: float = Field(default_factory=lambda: float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.75")))
    DEEPFAKE_THRESHOLD: float = 0.8
    VOICE_CLONE_THRESHOLD: float = 0.75

    # Trust Score Weights
    RESUME_WEIGHT: float = 0.3
    VIDEO_WEIGHT: float = 0.4
    AUDIO_WEIGHT: float = 0.3

    # Hugging Face AI Settings
    HUGGINGFACE_API_KEY: str = Field(default="")
    HF_API_URL: str = Field(default="https://api-inference.huggingface.co/models")
    AI_DETECTION_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("AI_DETECTION_ENABLED", "true").lower() == "true")
    AI_CACHE_ENABLED: bool = Field(default_factory=lambda: os.getenv("AI_CACHE_ENABLED", "true").lower() == "true")
    AI_CACHE_DURATION: int = Field(default_factory=lambda: int(os.getenv("AI_CACHE_DURATION", "3600")))

    # AI Model Configuration
    HF_AI_DETECTOR_MODEL: str = Field(default="Hello-SimpleAI/chatgpt-detector-roberta")
    HF_TEXT_CLASSIFIER_MODEL: str = Field(default="microsoft/DialoGPT-medium")
    HF_CONTENT_ANALYZER_MODEL: str = Field(default="cardiffnlp/twitter-roberta-base-sentiment-latest")

    # AI Detection Parameters
    AI_ENSEMBLE_WEIGHT: float = Field(default_factory=lambda: float(os.getenv("AI_ENSEMBLE_WEIGHT", "0.7")))
    RULE_BASED_WEIGHT: float = Field(default_factory=lambda: float(os.getenv("RULE_BASED_WEIGHT", "0.3")))
    MAX_RETRIES: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    TIMEOUT_SECONDS: int = Field(default_factory=lambda: int(os.getenv("TIMEOUT_SECONDS", "30")))

    # NEW: Job Posting Analysis Settings
    JOB_POSTING_ANALYSIS_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("JOB_POSTING_ANALYSIS_ENABLED", "true").lower() == "true")
    OCR_ENABLED: bool = Field(default_factory=lambda: os.getenv("OCR_ENABLED", "true").lower() == "true")
    WEB_SCRAPING_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("WEB_SCRAPING_ENABLED", "true").lower() == "true")
    COMPANY_VERIFICATION_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("COMPANY_VERIFICATION_ENABLED", "true").lower() == "true")

    # Web Intelligence Settings
    MAX_URL_LENGTH: int = 2048
    WEB_REQUEST_TIMEOUT: int = 30
    MAX_REDIRECT_FOLLOWS: int = 5

    # Development
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
