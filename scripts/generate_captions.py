import sys
import os
import subprocess
import json


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.logger import log

CLIPS_DIR = os.path.join(BASE_DIR, "clips")
CAPTIONS_DIR = os.path.join(BASE_DIR, "captions")
TRANSCRIPTS_PATH = os.path.join(CAPTIONS_DIR, "transcripts.json")

os.makedirs(CAPTIONS_DIR, exist_ok=True)

# Clean old caption artifacts
for f in os.listdir(CAPTIONS_DIR):
    if f.endswith((".srt", ".vtt", ".tsv", ".txt")):
        try:
            os.remove(os.path.join(CAPTIONS_DIR, f))
        except Exception:
            pass


def main():
    clips = sorted(f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4"))

    transcripts = {}

    if os.path.exists(TRANSCRIPTS_PATH):
        with open(TRANSCRIPTS_PATH, "r") as f:
            transcripts = json.load(f)

    if not clips:
        log.warning("No clips found to caption.")
        return

    for clip in clips:
        clip_path = os.path.join(CLIPS_DIR, clip)
        base = os.path.splitext(clip)[0]
        srt_path = os.path.join(CAPTIONS_DIR, f"{base}.srt")

        log.info(f"Generating captions for {clip}")

        whisper_cmd = [
            "whisper",
            clip_path,
            "--model", "small",
            "--language", "en",
            "--output_format", "srt",
            "--output_dir", CAPTIONS_DIR,
            "--verbose", "False"
        ]

        subprocess.run(whisper_cmd, check=True)

        if os.path.exists(srt_path):
            with open(srt_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                transcripts[clip] = text if len(text) > 30 else ""
        else:
            transcripts[clip] = ""

        if not os.path.exists(srt_path):
            log.error(f"SRT not generated for {clip}, skipping.")
            continue

        # 2. Burn captions into video
        output_path = os.path.join(CLIPS_DIR, f"{base}_captioned.mp4")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", clip_path,
            "-vf", f"subtitles='{srt_path}':force_style='FontSize=12,Alignment=2'",
            "-c:a", "copy",
            output_path
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        # 3. Replace original clip
        os.replace(output_path, clip_path)
        os.remove(srt_path)

        log.info(f"Captions applied to {clip}")

    with open(TRANSCRIPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(transcripts, f, indent=2, ensure_ascii=False)

    log.info(f"Saved transcripts to {TRANSCRIPTS_PATH}")


if __name__ == "__main__":
    main()