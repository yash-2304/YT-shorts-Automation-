import os
import random
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CLIPS_DIR = BASE_DIR / "clips"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "final_outputs"

GAMEPLAY_VIDEO = ASSETS_DIR / "subway_raw.mp4"  # change if filename differs

OUTPUT_DIR.mkdir(exist_ok=True)

def get_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip())

def main():
    if not GAMEPLAY_VIDEO.exists():
        raise FileNotFoundError(f"Gameplay video not found: {GAMEPLAY_VIDEO}")

    gameplay_duration = get_duration(GAMEPLAY_VIDEO)

    clips = sorted([f for f in CLIPS_DIR.iterdir() if f.suffix == ".mp4"])
    if not clips:
        raise RuntimeError("No clips found to stack")

    for clip in clips:
        clip_duration = get_duration(clip)

        max_start = max(0, gameplay_duration - clip_duration)
        start_time = random.uniform(0, max_start)

        output_path = OUTPUT_DIR / clip.name

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(GAMEPLAY_VIDEO),
            "-i", str(clip),
            "-filter_complex",
            (
                "[0:v]scale=1080:960:force_original_aspect_ratio=increase,"
                "crop=1080:960:(iw-1080)/2:(ih-960)/2,setsar=1[bottom];"
                "[1:v]scale=1080:960:force_original_aspect_ratio=increase,"
                "crop=1080:960:(iw-1080)/2:(ih-960)/2,setsar=1[top];"
                "[top][bottom]vstack=inputs=2[outv]"
            ),
            "-map", "[outv]",
            "-map", "1:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        print(f"✅ Stacked short created: {output_path.name}")

if __name__ == "__main__":
    main()