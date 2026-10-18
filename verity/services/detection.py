import logging
import re
import string
import tempfile
from pathlib import Path

import numpy as np

from ..errors import DetectionError

logger = logging.getLogger(__name__)


def clean_text(text):
    from nltk.corpus import stopwords

    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[%s]" % re.escape(string.punctuation), "", text)
    text = re.sub(r"\w*\d\w*", "", text)
    return " ".join(
        word
        for word in text.split()
        if word not in stopwords.words("english")
    )


def normalize_label(label):
    label = label.lower()
    if any(term in label for term in ("ai", "fake", "spoof", "synth")):
        return "AI"
    return "REAL"


def detect_ai_image(image_path, image_models):
    if not image_models:
        raise DetectionError("Image analysis is currently unavailable. Please try again later.")

    from PIL import Image

    try:
        with Image.open(image_path) as source_image:
            image = source_image.convert("RGB")
    except (OSError, ValueError) as error:
        raise DetectionError("The uploaded file could not be read as an image.") from error

    votes = []
    confidences = []
    last_error = None

    for name, model in image_models.items():
        try:
            result = model(image)[0]
            label = normalize_label(result["label"])
            score = result["score"]
            votes.append(label)
            confidences.append(score)
            logger.info("[IMAGE] %s: %s (%.2f)", name, label, score)
        except Exception as error:
            last_error = error
            logger.exception("[IMAGE] %s analysis failed", name)

    if not votes:
        raise DetectionError(
            "Image analysis failed. Please try again later."
        ) from last_error

    final_label = max(set(votes), key=votes.count)
    average_confidence = np.mean(
        [score for vote, score in zip(votes, confidences) if vote == final_label]
    )
    return final_label, round(average_confidence * 100, 2)


def detect_ai_audio(audio_path, audio_models):
    if not audio_models:
        raise DetectionError("Audio analysis is currently unavailable. Please try again later.")

    try:
        import librosa

        audio, _ = librosa.load(audio_path, sr=16000, mono=True)
        audio, _ = librosa.effects.trim(audio)
        votes = []
        confidences = []

        for model in audio_models:
            outputs = model(audio)
            for output in outputs:
                label = normalize_label(output["label"])
                score = output["score"]
                votes.append(label)
                confidences.append(score)
                logger.info("[AUDIO] %s (%.2f)", label, score)
                break

        if not votes:
            raise DetectionError("Audio analysis returned no result. Please try again.")

        final_label = max(set(votes), key=votes.count)
        average_confidence = np.mean(
            [score for vote, score in zip(votes, confidences) if vote == final_label]
        )
        return final_label, round(average_confidence * 100, 2)
    except DetectionError:
        raise
    except Exception as error:
        logger.exception("Audio analysis failed")
        raise DetectionError("Audio analysis failed. Please try again later.") from error


def detect_ai_video(video_path, models, upload_folder):
    try:
        from moviepy.editor import VideoFileClip

        with tempfile.TemporaryDirectory(dir=upload_folder) as work_dir:
            frame_path = str(Path(work_dir) / "frame.jpg")
            audio_path = str(Path(work_dir) / "audio.wav")
            video = VideoFileClip(video_path)
            try:
                video.save_frame(frame_path, t=1)
                frame_label, frame_confidence = detect_ai_image(
                    frame_path,
                    models["image_models"],
                )

                audio_label, audio_confidence = "REAL", 50.0
                if video.audio:
                    video.audio.write_audiofile(
                        audio_path,
                        verbose=False,
                        logger=None,
                    )
                    audio_label, audio_confidence = detect_ai_audio(
                        audio_path,
                        models["audio_models"],
                    )
            finally:
                video.close()

        labels = [frame_label, audio_label]
        confidences = [frame_confidence, audio_confidence]
        final_label = max(set(labels), key=labels.count)
        final_confidence = round(np.mean(confidences), 2)
        logger.info("[VIDEO] Frame=%s, Audio=%s", frame_label, audio_label)
        return final_label, final_confidence
    except DetectionError:
        raise
    except Exception as error:
        logger.exception("Video analysis failed")
        raise DetectionError("Video analysis failed. Please try again later.") from error
