import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from verity import create_app
from verity.config import Config
from verity.errors import DetectionError


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.uploads = tempfile.TemporaryDirectory()

        class TestConfig(Config):
            TESTING = True
            SECRET_KEY = "test"
            UPLOAD_FOLDER = self.uploads.name
            DETECTION_MODELS = {
                "news_model": None,
                "news_vectorizer": None,
                "image_models": {},
                "audio_models": [],
            }

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        self.uploads.cleanup()

    def test_existing_pages_render(self):
        for path in ("/", "/check_news", "/check_image", "/check_audio", "/check_video"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_uploaded_file_is_removed_after_analysis(self):
        with patch(
            "verity.routes.detect_ai_image",
            return_value=("AI", 91.0),
        ) as detect_image:
            response = self.client.post(
                "/check_image",
                data={"image": (BytesIO(b"test image"), "../../sample.png")},
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        analyzed_path = Path(detect_image.call_args.args[0])
        self.assertEqual(analyzed_path.parent, Path(self.uploads.name))
        self.assertFalse(analyzed_path.exists())
        self.assertEqual(list(Path(self.uploads.name).iterdir()), [])

    def test_analysis_failure_shows_message_and_cleans_upload(self):
        with patch(
            "verity.routes.detect_ai_image",
            side_effect=DetectionError("Image analysis is unavailable."),
        ):
            response = self.client.post(
                "/check_image",
                data={"image": (BytesIO(b"test image"), "sample.png")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image analysis is unavailable.", response.data)
        self.assertEqual(list(Path(self.uploads.name).iterdir()), [])

    def test_unconfigured_image_detector_reports_unavailable(self):
        response = self.client.post(
            "/check_image",
            data={"image": (BytesIO(b"test image"), "sample.png")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image analysis is currently unavailable.", response.data)
        self.assertEqual(list(Path(self.uploads.name).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
