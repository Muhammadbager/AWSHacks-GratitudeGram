"""Thin wrapper around the two Bedrock calls GratitudeGram needs."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass

import boto3

AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")

# Claude Sonnet 4.5 via the US cross-region inference profile.
TEXT_MODEL_ID = os.environ.get(
    "GG_TEXT_MODEL_ID",
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
)

# Stability AI's Stable Image Core for the card illustration.
# It's fast (~3-5s), cheap, and produces lovely watercolor-style art.
IMAGE_MODEL_ID = os.environ.get(
    "GG_IMAGE_MODEL_ID", "stability.stable-image-core-v1:1"
)

_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)


@dataclass
class LetterRequest:
    author_name: str
    recipient_name: str
    relationship: str
    why: str
    memories: str
    tone: str  # "heartfelt" | "funny" | "formal"


SYSTEM_PROMPT = """You are a thoughtful ghost writer helping someone express
deep gratitude to a person who shaped their life. Write a thank-you letter in
the writer's voice, using ONLY the facts they give you.

Rules:
- Write in first person ("I").
- Weave in the specific memories naturally; don't list them.
- Avoid clichés ("words can't express", "from the bottom of my heart", "you
  mean the world to me"). Be specific, not generic.
- Length: 150-220 words.
- Open with the recipient's name on its own line (e.g. "Dear Mom,").
- Close with a warm sign-off and the writer's first name on its own line.
- Match the requested tone exactly.
- Never invent facts. If a detail is missing, write around it.
- Output the letter only. No preamble, no explanation, no markdown."""


def _build_user_prompt(req: LetterRequest) -> str:
    return (
        f"Writer's name: {req.author_name or '(unspecified)'}\n"
        f"Recipient: {req.recipient_name}\n"
        f"Relationship: {req.relationship}\n"
        f"What they did / why I'm grateful: {req.why}\n"
        f"Specific memories or qualities:\n{req.memories}\n"
        f"Tone: {req.tone}\n"
    )


def generate_letter(req: LetterRequest) -> str:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 700,
        "temperature": 0.7,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": _build_user_prompt(req)}],
    }
    response = _runtime.invoke_model(
        modelId=TEXT_MODEL_ID,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    return payload["content"][0]["text"].strip()


# Style cues fed to the image model so cards feel like physical greeting cards.
_IMAGE_STYLE = (
    "soft watercolor illustration, warm pastel colors, gentle natural light, "
    "elegant minimal composition, centered subject, plenty of empty space at "
    "the top and bottom for handwritten text, no text in the image, no words, "
    "no letters, print-ready greeting card art"
)


def _build_image_prompt(req: LetterRequest) -> str:
    return (
        f"A heartfelt greeting card illustration that evokes gratitude toward "
        f"a {req.relationship.lower() or 'loved one'}. "
        f"Inspired by these memories: {req.memories}. "
        f"{_IMAGE_STYLE}."
    )


def generate_card_image(req: LetterRequest) -> bytes:
    """Returns raw PNG bytes for the card illustration."""
    prompt = _build_image_prompt(req)
    # Stability's unified text-to-image API (Stable Image Core / Ultra / SD3.5).
    body = {
        "prompt": prompt[:9000],
        "negative_prompt": (
            "text, words, letters, typography, watermark, signature, "
            "logo, low quality, blurry, distorted faces, deformed"
        ),
        "aspect_ratio": "3:2",
        "output_format": "png",
        "seed": 0,  # 0 = random
    }
    response = _runtime.invoke_model(
        modelId=IMAGE_MODEL_ID,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    if not payload.get("images"):
        finish = payload.get("finish_reasons", ["unknown"])[0]
        raise RuntimeError(f"Image generation returned no image (reason: {finish})")
    b64_png = payload["images"][0]
    return base64.b64decode(b64_png)
