"""GratitudeGram — AI-generated thank-you cards, powered by Amazon Bedrock."""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from bedrock_client import LetterRequest, generate_card_image, generate_letter

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gratitudegram")

BASE_DIR = Path(__file__).parent
CARDS_DIR = BASE_DIR / "static" / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def _parse_request() -> LetterRequest:
    data = request.get_json(force=True) or {}
    return LetterRequest(
        author_name=(data.get("author_name") or "").strip(),
        recipient_name=(data.get("recipient_name") or "").strip(),
        relationship=(data.get("relationship") or "").strip(),
        why=(data.get("why") or "").strip(),
        memories=(data.get("memories") or "").strip(),
        tone=(data.get("tone") or "heartfelt").strip().lower(),
    )


@app.post("/api/letter")
def api_letter():
    req = _parse_request()
    if not req.recipient_name or not req.why:
        return jsonify({"error": "recipient_name and why are required"}), 400
    try:
        t0 = time.time()
        letter = generate_letter(req)
        log.info("letter generated in %.1fs", time.time() - t0)
        return jsonify({"letter": letter})
    except Exception as exc:  # surface Bedrock errors to the UI
        log.exception("letter generation failed")
        return jsonify({"error": str(exc)}), 500


@app.post("/api/card")
def api_card():
    req = _parse_request()
    if not req.recipient_name:
        return jsonify({"error": "recipient_name is required"}), 400
    try:
        t0 = time.time()
        png_bytes = generate_card_image(req)
        filename = f"{uuid.uuid4().hex}.png"
        (CARDS_DIR / filename).write_bytes(png_bytes)
        log.info("card generated in %.1fs", time.time() - t0)
        return jsonify({"image_url": f"/static/cards/{filename}"})
    except Exception as exc:
        log.exception("card generation failed")
        return jsonify({"error": str(exc)}), 500


@app.route("/static/cards/<path:filename>")
def serve_card(filename: str):
    return send_from_directory(CARDS_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
