import sys
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_ROOT = PROJECT_ROOT / "input"
CLIPS_DIR = PROJECT_ROOT / "clips"
CAPTIONS_DIR = PROJECT_ROOT / "captions"
FINAL_DIR = PROJECT_ROOT / "final_outputs"
LOGS_DIR = PROJECT_ROOT / "logs"

def run(cmd, desc=None):
    if desc:
        print(f"▶️ {desc}")
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 run_pipeline.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    today = datetime.now().strftime("%Y-%m-%d")

    input_dir = INPUT_ROOT / today
    input_dir.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    print(f"📥 INPUT DIR: {input_dir}")

    # 1️⃣ Download YouTube video
    run([
        "yt-dlp",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", f"{input_dir}/%(title)s.%(ext)s",
        youtube_url
    ], "Downloading YouTube video")

    videos = (
        list(input_dir.glob("*.mp4"))
        + list(input_dir.glob("*.mkv"))
        + list(input_dir.glob("*.webm"))
    )
    if not videos:
        print("❌ No video downloaded")
        sys.exit(1)

    input_video = videos[0]

    # Ensure MP4 input for downstream scripts
    if input_video.suffix == ".webm":
        mp4_video = input_video.with_suffix(".mp4")
        run([
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-c:v", "libx264",
            "-c:a", "aac",
            str(mp4_video)
        ], "Converting WEBM to MP4")
        input_video.unlink()
        input_video = mp4_video

    print(f"🎬 Using video: {input_video.name}")

    # ==============================
    # PRE-RUN CLEANUP (REMOVE OLD OUTPUTS)
    # ==============================
    print("🧹 Clearing old clips and outputs...")

    for folder in [CLIPS_DIR, FINAL_DIR, CAPTIONS_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)

    print("✅ Old generated files cleared")

    # 3️⃣ Create clips
    run([
        "python3",
        "scripts/clips.py",
        str(input_video)
    ], "Creating shorts")

    # 4️⃣ Generate captions + transcripts
    run([
        "python3",
        "scripts/generate_captions.py"
    ], "Generating captions")

    # Safety log before title generation
    print("🧠 Transcripts ready — generating titles")

    # 5️⃣ Generate titles
    run([
        "python3",
        "scripts/generate_titles.py"
    ], "Generating titles")

    # 5️⃣½ Stack gameplay clip (Minecraft/Subway/etc)
    run([
        "python3",
        "scripts/stack_clips.py"
    ], "Stacking gameplay clips")


    # 7️⃣ Upload shorts to YouTube
    run([
        "python3",
        "scripts/upload_shorts.py"
    ], "Uploading Shorts to YouTube")

    # ==============================
    # FINAL CLEANUP (SAFE)
    # ==============================
    print("🧹 Final cleanup starting...")

    transcripts_path = CAPTIONS_DIR / "transcripts.json"

    if transcripts_path.exists():
        transcripts_path.unlink()
        print(f"🗑️ Removed {transcripts_path}")

    print("✅ Pipeline completed successfully")

if __name__ == "__main__":
    main()