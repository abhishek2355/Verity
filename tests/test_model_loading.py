import logging
import sys
import unittest
from unittest.mock import patch

from verity.services.models import load_models


class ModelLoadingTests(unittest.TestCase):
    def test_disabled_media_models_do_not_import_torch_or_transformers(self):
        config = {
            "NEWS_MODEL_PATH": "fake_news_model.pkl",
            "NEWS_VECTORIZER_PATH": "tfidf_vectorizer.pkl",
            "ENABLE_IMAGE_MODELS": False,
            "ENABLE_AUDIO_MODELS": False,
            "IMAGE_MODEL_LIST": (("test", "test-model"),),
            "AUDIO_MODEL_LIST": ("test-audio-model",),
        }

        with (
            patch("joblib.load", side_effect=[object(), object()]),
            patch.dict(sys.modules, {"torch": None, "transformers": None}),
        ):
            models = load_models(config, logging.getLogger(__name__))

        self.assertEqual(models["image_models"], {})
        self.assertEqual(models["audio_models"], [])
        self.assertIsNotNone(models["news_model"])
        self.assertIsNotNone(models["news_vectorizer"])


if __name__ == "__main__":
    unittest.main()
