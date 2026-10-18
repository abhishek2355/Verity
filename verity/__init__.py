import logging
from pathlib import Path

from flask import Flask

from .config import Config
from .routes import main
from .services.models import load_models

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app(config_object=Config):
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
    )
    app.config.from_object(config_object)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    if not app.testing:
        logging.basicConfig(level=app.config["LOG_LEVEL"])
        import nltk

        nltk.download("stopwords", quiet=True)

    if app.testing:
        app.extensions["detection_models"] = app.config.get(
            "DETECTION_MODELS",
            {
                "news_model": None,
                "news_vectorizer": None,
                "image_models": {},
                "audio_models": [],
            },
        )
    else:
        app.extensions["detection_models"] = load_models(app.config, app.logger)
    app.register_blueprint(main)
    return app
