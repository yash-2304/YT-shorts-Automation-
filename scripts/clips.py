import sys
import json
import subprocess
import os
from datetime import date
import whisper
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_root = os.path.join(BASE_DIR, "input")

if not os.path.exists(input_root):
    print(f"❌ Input root directory not found: {input_root}")
    sys.exit(1)

date_folders = sorted(
    [
        d for d in os.listdir(input_root)
        if os.path.isdir(os.path.join(input_root, d))
    ],
    reverse=True
)

if not date_folders:
    print("❌ No dated input folders found in input/")
    sys.exit(1)

input_dir = os.path.join(input_root, date_folders[0])
print(f"📂 Using latest input folder: {input_dir}")

mp4_files = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]
if not mp4_files:
    print(f"❌ No .mp4 files found in {input_dir}")
    sys.exit(1)

INPUT_VIDEO = os.path.join(input_dir, mp4_files[0])

CLIP_LENGTH = 30

INTRO_SKIP = 90
OUTRO_SKIP = 60
MIN_CLIPS = 5

OUTPUT_DIR = os.path.join(BASE_DIR, "clips")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🎬 Using input video: {INPUT_VIDEO}")

for f in os.listdir(OUTPUT_DIR):
    if f.endswith(".mp4"):
        os.remove(os.path.join(OUTPUT_DIR, f))

def get_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

duration = get_duration(INPUT_VIDEO)
usable_start = INTRO_SKIP
usable_end = duration - OUTRO_SKIP

available_window = usable_end - usable_start
max_possible_clips = int(available_window // CLIP_LENGTH)

if max_possible_clips < MIN_CLIPS:
    print(f"❌ Not enough usable video to generate {MIN_CLIPS} clips")
    sys.exit(1)

def transcribe_usable_section(video_path, start, end):
    model = whisper.load_model("small")
    result = model.transcribe(
        video_path,
        fp16=False,
        initial_prompt="Esports commentary with hype moments",
        condition_on_previous_text=False
    )
    segments = []
    for seg in result["segments"]:
        if start <= seg["start"] <= end:
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].lower()
            })
    return segments


HYPE_WORDS = [
    "clutch", "insane", "what a", "unbelievable", "huge",
    "crazy", "steals", "finishes", "down goes", "wins",
    "ace", "destroyed", "one more", "no way"
]


def score_segments(segments):
    scored = []
    for seg in segments:
        score = 0
        for w in HYPE_WORDS:
            if w in seg["text"]:
                score += 3
        score += seg["text"].count("!") * 2
        score += len(seg["text"].split()) // 10
        scored.append({**seg, "score": score})
    return sorted(scored, key=lambda x: x["score"], reverse=True)

print("🧠 Transcribing usable video section with Whisper...")
segments = transcribe_usable_section(INPUT_VIDEO, usable_start, usable_end)

scored_segments = score_segments(segments)

if len(scored_segments) < MIN_CLIPS:
    print("❌ Not enough highlight segments found")
    sys.exit(1)

starts = []
for seg in scored_segments[:MIN_CLIPS]:
    center = (seg["start"] + seg["end"]) / 2
    clip_start = max(usable_start, center - CLIP_LENGTH / 2)
    starts.append(clip_start)

for i, start in enumerate(starts, 1):
    output = f"{OUTPUT_DIR}/short_{i}.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", INPUT_VIDEO,
        "-t", str(CLIP_LENGTH),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output
    ], check=True)

    print(f"✅ Created {output}")