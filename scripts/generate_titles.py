import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.logger import log

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=OPENAI_API_KEY)

CLIPS_DIR = PROJECT_ROOT / "final_outputs"
CAPTIONS_DIR = PROJECT_ROOT / "captions"
TRANSCRIPTS_PATH = CAPTIONS_DIR / "transcripts.json"
OUTPUT_FILE = PROJECT_ROOT / "titles.json"
TITLE_STYLE = "mix"  # mix | dramatic | informational


def generate_title(transcript):
    style_instruction = {
        "mix": (
            "Adapt the title style based on content. "
            "For gaming: hype/clutch. "
            "For podcasts/business: thought-provoking. "
            "For conspiracy: mysterious. "
            "For food: satisfying or curiosity-driven."
        ),
        "dramatic": "Make the title highly emotional, shocking, or suspenseful.",
        "informational": "Make the title clear, smart, and insight-focused."
    }.get(TITLE_STYLE, "mix")

    prompt = f"""
You are an expert YouTube Shorts growth strategist.

STYLE:
{style_instruction}

TASK:
Write ONE viral YouTube Shorts title from the transcript below.

RULES:
- 4–8 words only
- No emojis
- No hashtags
- No clickbait phrases like 'you won’t believe'
- Must trigger curiosity or emotion
- Natural human tone

TRANSCRIPT:
{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.95,
        max_tokens=16,
    )

    return response.choices[0].message.content.strip().replace('"', '')

def main():
    titles = {}

    # ==============================
    # Load and normalize transcripts
    # ==============================
    if TRANSCRIPTS_PATH.exists():
        with open(TRANSCRIPTS_PATH, "r", encoding="utf-8") as f:
            raw_transcripts = json.load(f)
        print(f"✅ Loaded transcripts from {TRANSCRIPTS_PATH}")
    else:
        print(f"⚠️ transcripts.json not found at {TRANSCRIPTS_PATH}, falling back to clip names")
        raw_transcripts = {}

    # Normalize transcript keys to always include .mp4
    transcripts = {}
    for k, v in raw_transcripts.items():
        if k.endswith(".mp4"):
            transcripts[k] = v
        else:
            transcripts[f"{k}.mp4"] = v

    print(f"🔧 Normalized transcript keys: {list(transcripts.keys())}")

    if not CLIPS_DIR.exists():
        raise FileNotFoundError(f"Clips directory not found at {CLIPS_DIR}")

    for clip in sorted(os.listdir(CLIPS_DIR)):
        if not clip.endswith(".mp4"):
            continue

        transcript = transcripts.get(clip, "")
        if transcript and len(transcript.strip()) > 40:
            print(f"ℹ️ Transcript found for {clip}")
            try:
                title = generate_title(transcript)
            except Exception as e:
                log.error(f"OpenAI title generation failed for {clip}: {e}")
                base = os.path.splitext(clip)[0].replace("_", " ").title()
                title = f"{base} Highlight"
        else:
            print(f"⚠️ No transcript found for {clip}, using fallback")
            base = os.path.splitext(clip)[0].replace("_", " ").title()
            title = f"{base} Highlight"

        titles[clip] = title
        print(f"🎯 {clip} → {title}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(titles, f, indent=2)

    print(f"📄 Titles saved to {OUTPUT_FILE}")

    print("✅ titles.json generated")

if __name__ == "__main__":
    main()