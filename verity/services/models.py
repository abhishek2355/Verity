def load_models(config, logger):
    models = {
        "news_model": None,
        "news_vectorizer": None,
        "image_models": {},
        "audio_models": [],
    }

    try:
        import joblib

        models["news_model"] = joblib.load(config["NEWS_MODEL_PATH"])
        models["news_vectorizer"] = joblib.load(config["NEWS_VECTORIZER_PATH"])
        logger.info("Fake news model loaded")
    except Exception:
        models["news_model"] = None
        models["news_vectorizer"] = None
        logger.exception("Fake news model could not be loaded")

    from transformers import pipeline

    logger.info("Loading image detection models")
    for name, model_id in config["IMAGE_MODEL_LIST"]:
        try:
            models["image_models"][name] = pipeline(
                "image-classification",
                model=model_id,
            )
            logger.info("Image model loaded: %s", name)
        except Exception:
            logger.exception("Image model failed to load: %s", name)

    logger.info("Loading audio detection models")
    try:
        import torch
    except Exception:
        logger.exception("PyTorch could not be imported; audio models are unavailable")
        return models

    device = 0 if torch.cuda.is_available() else -1
    for model_id in config["AUDIO_MODEL_LIST"]:
        try:
            models["audio_models"].append(
                pipeline(
                    "audio-classification",
                    model=model_id,
                    device=device,
                )
            )
            logger.info("Audio model loaded: %s", model_id)
        except Exception:
            logger.exception("Audio model failed to load: %s", model_id)

    return models
