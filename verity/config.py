import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _enabled(name, default=True):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "your_secret_key")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(PROJECT_ROOT / "uploads"))
    NEWS_MODEL_PATH = PROJECT_ROOT / "fake_news_model.pkl"
    NEWS_VECTORIZER_PATH = PROJECT_ROOT / "tfidf_vectorizer.pkl"
    ENABLE_IMAGE_MODELS = _enabled("ENABLE_IMAGE_MODELS")
    ENABLE_AUDIO_MODELS = _enabled("ENABLE_AUDIO_MODELS")
    IMAGE_MODEL_LIST = (("Ateeqq", "Ateeqq/ai-vs-human-image-detector"),)
    AUDIO_MODEL_LIST = ("Hemgg/Deepfake-audio-detection",)
