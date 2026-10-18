import os
import tempfile
from pathlib import Path

import numpy as np
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from .errors import DetectionError
from .reasons import FakeNewsReasons
from .services.detection import (
    clean_text,
    detect_ai_audio,
    detect_ai_image,
    detect_ai_video,
)

main = Blueprint("main", __name__)


def _models():
    return current_app.extensions["detection_models"]


def _save_upload(upload):
    if upload is None or not upload.filename:
        return None

    safe_name = secure_filename(upload.filename)
    suffix = Path(safe_name).suffix
    descriptor, path = tempfile.mkstemp(
        prefix="upload_",
        suffix=suffix,
        dir=current_app.config["UPLOAD_FOLDER"],
    )
    os.close(descriptor)
    try:
        upload.save(path)
    except Exception:
        Path(path).unlink(missing_ok=True)
        raise
    return path


def _remove_upload(path):
    if path:
        Path(path).unlink(missing_ok=True)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/check_news", methods=["GET", "POST"])
def check_news():
    if request.method == "POST":
        models = _models()
        model = models["news_model"]
        vectorizer = models["news_vectorizer"]
        if model is None or vectorizer is None:
            flash("Fake news model not loaded")
            return redirect(url_for("main.check_news"))

        title = request.form.get("title", "")
        article = request.form.get("article", "")
        text = clean_text(title + " " + article)
        if len(text.split()) < 5:
            flash("Please enter more meaningful text")
            return redirect(url_for("main.check_news"))

        vectorized_text = vectorizer.transform([text])
        prediction = model.predict(vectorized_text)[0]
        probabilities = model.predict_proba(vectorized_text)[0]
        label = "REAL" if prediction == 1 else "FAKE"
        confidence = round(np.max(probabilities) * 100, 2)

        return render_template(
            "result_news.html",
            label=label,
            confidence=confidence,
            reason=FakeNewsReasons.get_reason(label, "news"),
        )

    return render_template("check_news.html")


@main.route("/check_image", methods=["GET", "POST"])
def check_image():
    if request.method == "POST":
        path = _save_upload(request.files.get("image"))
        if path is None:
            flash("No image uploaded")
            return redirect(url_for("main.check_image"))
        try:
            label, confidence = detect_ai_image(path, _models()["image_models"])
        except DetectionError as error:
            flash(str(error))
            return redirect(url_for("main.check_image"))
        finally:
            _remove_upload(path)

        return render_template(
            "result_image.html",
            label=label,
            confidence=f"{confidence}%",
            reason=FakeNewsReasons.get_reason(label, "image"),
        )

    return render_template("check_image.html")


@main.route("/check_audio", methods=["GET", "POST"])
def check_audio():
    if request.method == "POST":
        path = _save_upload(request.files.get("audio"))
        if path is None:
            flash("No audio uploaded")
            return redirect(url_for("main.check_audio"))
        try:
            label, confidence = detect_ai_audio(path, _models()["audio_models"])
        except DetectionError as error:
            flash(str(error))
            return redirect(url_for("main.check_audio"))
        finally:
            _remove_upload(path)

        return render_template(
            "result_audio.html",
            label=label,
            confidence=f"{confidence}%",
            reason=FakeNewsReasons.get_reason(label, "audio"),
        )

    return render_template("check_audio.html")


@main.route("/check_video", methods=["GET", "POST"])
def check_video():
    if request.method == "POST":
        path = _save_upload(request.files.get("video"))
        if path is None:
            flash("No video uploaded")
            return redirect(url_for("main.check_video"))
        try:
            label, confidence = detect_ai_video(
                path,
                _models(),
                current_app.config["UPLOAD_FOLDER"],
            )
        except DetectionError as error:
            flash(str(error))
            return redirect(url_for("main.check_video"))
        finally:
            _remove_upload(path)

        return render_template(
            "result_video.html",
            label=label,
            confidence=f"{confidence}%",
            reason=FakeNewsReasons.get_reason(label, "video"),
        )

    return render_template("check_video.html")
