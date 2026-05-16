from pathlib import Path

from bedrock_client import LetterRequest, generate_card_image

req = LetterRequest(
    author_name="Alex",
    recipient_name="Grandma Rose",
    relationship="my grandmother",
    why="She taught me to read in two languages.",
    memories="Sunday pancakes, Tagalog bedtime stories, warm hugs",
    tone="heartfelt",
)

png = generate_card_image(req)
out = Path("static/cards/_smoke.png")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(png)
print(f"Wrote {len(png)} bytes to {out}")
