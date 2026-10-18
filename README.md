# Verity

Verity is a Flask application for AI-assisted analysis of news text, images, audio, and video. Results are estimates, not definitive proof; verify important claims with trusted sources.

## Screenshots

### Dashboard

![Verity dashboard](docs/screenshots/dashboard.png)

### News analysis

<table>
  <tr>
    <td align="center"><strong>Submit a story</strong></td>
    <td align="center"><strong>Analysis result</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/news-check.png" alt="News analysis form" width="100%"></td>
    <td><img src="docs/screenshots/analysis-result.png" alt="News analysis result" width="100%"></td>
  </tr>
</table>

### Image analysis

![Image analysis upload form](docs/screenshots/image-check.png)

## Features

- Analyze news headlines and article text.
- Check images for possible AI-generation signals.
- Analyze audio for possible synthetic speech.
- Review video using visual-frame and audio analysis.

## Run locally

Use Python 3.11. From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The first launch may take a while because the image and audio models are downloaded on startup; an internet connection is required.

## Deploy on Render

The repository includes a Render Blueprint in `render.yaml`. To create a free demo deployment:

1. Push or merge this configuration to the repository's `main` branch.
2. In the [Render Dashboard](https://dashboard.render.com/), select **New → Blueprint** and connect this repository.
3. Review the `verity` web service and click **Apply**. Render generates the Flask secret and provides a public `onrender.com` URL when deployment succeeds.

The free Render configuration installs only the dependencies needed for news text analysis and disables the image, audio, and video models to stay within the free instance's memory limit; **news text analysis is the only enabled detector**. Free services can sleep when idle, their local files are temporary, and the first boot can be slow. To enable image/audio/video detection, use a paid instance, switch the Render build command to `pip install -r requirements.txt`, and set `ENABLE_IMAGE_MODELS` and `ENABLE_AUDIO_MODELS` to `true`.
