# GratitudeGram

> Say thank you, beautifully. An AI-generated thank-you card service built on
> Amazon Bedrock for the **AWS Hackathon — Build with Gratitude (May 2026)**.

GratitudeGram takes a handful of plain-text answers — *who you're thanking,
why, and a few specific memories* — and produces a printable greeting card
with a personalized handwritten-style letter on one side and an original
watercolor illustration on the other. Two Bedrock models do the work:
**Claude Sonnet 4.5** writes the letter and **Stable Image Core** paints the
art.

## Team

- Muhammadbager Al-Ali
- Tri Vo

## Track

**Build with Bedrock.** Bedrock is the core service. The whole project hinges
on two model invocations chained from a small Flask backend.

## Theme alignment — "Build with Gratitude"

The product *is* the theme. Every interaction is a person being walked
through articulating gratitude they've been carrying around — the immigrant
grandmother, the coach who showed up, the friend who held the line. The app
lowers the cost of saying thank you well enough to actually send it.

## What was built (during the event)

- Web UI with a single-form, single-result flow.
- Flask backend with two JSON endpoints:
  - `POST /api/letter` → Claude Sonnet 4.5 via Bedrock.
  - `POST /api/card` → Stable Image Core via Bedrock; stores PNG in
    `static/cards/` and returns the URL.
- Prompt engineering for both models (system prompt for the letter, style
  guide for the illustration).
- Parallel API dispatch on the client so the letter and the artwork render
  together.
- Print-friendly CSS so the card prints as one page.

## What was not built (and why)

- **Serverless deployment.** Local Flask was prioritized so the demo would be
  rock-solid by submission. The codebase is already structured to drop into
  Lambda + API Gateway + S3 (see *Next steps*).
- **Auth / accounts.** Out of scope for a 24-hour build. Each card is
  ephemeral on the local filesystem.
- **Polly audio narration.** Considered but cut to keep the demo crisp.

## AWS services used

| Service                             | Role                                            |
| ----------------------------------- | ----------------------------------------------- |
| **Amazon Bedrock** (Claude Sonnet 4.5)   | Letter generation                          |
| **Amazon Bedrock** (Stable Image Core)   | Card illustration                           |
| _(Planned)_ AWS Lambda + API Gateway     | Serverless backend deploy                   |
| _(Planned)_ Amazon S3                    | Persistent storage of generated cards       |

## Pre-existing code / templates used

None. The project was scaffolded from an empty directory during the event.
The only dependency is the `boto3` SDK that was already installed for the
initial Bedrock smoke test (`test.py`).

## Architecture

```
┌──────────────┐    HTTPS     ┌──────────────┐  invoke_model  ┌────────────────┐
│  Browser UI  │ ───────────► │  Flask App   │ ─────────────► │  Amazon        │
│ (index.html) │              │  (app.py)    │                │  Bedrock       │
│              │ ◄─────────── │              │ ◄───────────── │                │
└──────────────┘   JSON       └──────┬───────┘  letter +      │  • Claude 4.5  │
                                     │           PNG bytes    │  • Stable Img  │
                                     ▼                        └────────────────┘
                              static/cards/*.png
                              (served back to browser)
```

(Hand-drawn version included in the submission.)

## Running locally

### 1. Prerequisites

- Python 3.10+
- An AWS account with Bedrock access in `us-west-2`, plus model access
  enabled for:
  - **Anthropic Claude Sonnet 4.5** (inference profile
    `us.anthropic.claude-sonnet-4-5-20250929-v1:0`)
  - **Stability AI Stable Image Core 1.0**
    (`stability.stable-image-core-v1:1`)
- AWS credentials configured (`aws configure`, an SSO session, or
  `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars).

### 2. Install

```powershell
python -m pip install -r requirements.txt
```

### 3. Run

```powershell
python app.py
```

Open <http://127.0.0.1:5000> and fill in the form.

### 4. (Optional) override models / region

```powershell
$env:AWS_REGION = "us-west-2"
$env:GG_TEXT_MODEL_ID  = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
$env:GG_IMAGE_MODEL_ID = "stability.stable-image-core-v1:1"
python app.py
```

## Project layout

```
.
├── app.py                  # Flask entry point + JSON endpoints
├── bedrock_client.py       # The two Bedrock invocations live here
├── requirements.txt
├── templates/
│   └── index.html          # Single-page UI
├── static/
│   ├── style.css
│   ├── app.js
│   └── cards/              # Generated PNGs land here
├── test.py                 # Original Bedrock connectivity smoke test
├── smoke_test.py           # Letter-only sanity check
└── smoke_test_image.py     # Image-only sanity check
```

## Next steps (if more time)

1. **Go fully serverless.** Wrap `bedrock_client.py` in a Lambda function,
   front it with API Gateway, and write generated PNGs to S3 (returning a
   pre-signed URL). The Flask code already isolates the Bedrock calls so this
   is a straight port.
2. **Polly narration.** Add an "Hear it read aloud" button that calls Amazon
   Polly with a neural voice, so the recipient can listen as well as read.
3. **Translation layer.** A second Claude call translating the letter into
   the recipient's preferred language with culturally appropriate tone
   (currently the strongest "v2" idea).
4. **Email delivery.** Hand the card off to Amazon SES so users can send it
   directly without screenshotting.

## Acknowledgements

This whole project is itself a thank you — to everyone who taught us to read,
to write, to build, and to take up space without apology.
