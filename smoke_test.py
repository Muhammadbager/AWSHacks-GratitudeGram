"""Quick offline sanity check before running the full app."""

from bedrock_client import LetterRequest, generate_letter

req = LetterRequest(
    author_name="Alex",
    recipient_name="Grandma Rose",
    relationship="my grandmother",
    why="She taught me to read in two languages and never let me feel small.",
    memories=(
        "- Sunday morning pancakes with too much cinnamon\n"
        "- Reading me 'Goodnight Moon' in Tagalog\n"
        "- Sneaking me extra dollars at every family party"
    ),
    tone="heartfelt",
)

print(generate_letter(req))
