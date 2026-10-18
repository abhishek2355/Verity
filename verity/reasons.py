import random


class FakeNewsReasons:
    FAKE_NEWS_REASONS = [
        "The article contains exaggerated or misleading claims.",
        "The content lacks credible and verifiable sources.",
        "The language used is emotionally manipulative.",
        "The information does not match trusted news databases.",
        "The article structure matches common fake news patterns.",
        "Suspicious wording and unsupported statements detected.",
        "Headline appears misleading compared to the content.",
        "Content includes unverifiable facts or altered data.",
    ]

    FAKE_IMAGE_REASONS = [
        "The image contains visual artifacts typical of AI generation.",
        "Inconsistent lighting and shadow patterns detected.",
        "Facial symmetry and texture patterns appear synthetic.",
        "Image metadata analysis suggests artificial generation.",
        "Background details show distortion common in AI images.",
        "Pixel-level irregularities detected in image structure.",
        "Unnatural blending between foreground and background.",
        "AI-generated texture patterns identified.",
    ]

    FAKE_AUDIO_REASONS = [
        "Voice waveform patterns indicate synthetic generation.",
        "Speech rhythm and tone variation appear artificial.",
        "Audio frequency spectrum matches AI-generated patterns.",
        "Lack of natural breathing and background noise detected.",
        "Voice modulation inconsistencies found.",
        "Audio artifacts typical of deepfake speech detected.",
        "Phoneme transitions appear mechanically generated.",
        "Unnatural pitch consistency detected.",
    ]

    FAKE_VIDEO_REASONS = [
        "Facial movements are inconsistent with natural expressions.",
        "Lip-sync mismatch detected between audio and video.",
        "Frame-level artifacts indicate possible manipulation.",
        "Background motion inconsistencies detected.",
        "Lighting changes are unnatural across frames.",
        "Deepfake blending artifacts detected.",
        "Video compression anomalies suggest tampering.",
        "Frame analysis shows synthetic generation patterns.",
    ]

    @staticmethod
    def get_reason(label, category):
        if label in {"FAKE", "AI"}:
            reasons = {
                "news": FakeNewsReasons.FAKE_NEWS_REASONS,
                "image": FakeNewsReasons.FAKE_IMAGE_REASONS,
                "audio": FakeNewsReasons.FAKE_AUDIO_REASONS,
                "video": FakeNewsReasons.FAKE_VIDEO_REASONS,
            }
            category_reasons = reasons.get(category)
            if category_reasons:
                return random.choice(category_reasons)

        return "No manipulation patterns were detected by the AI model."
