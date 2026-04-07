import sys
import os
import subprocess
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

BASE_INPUT_DIR = "input"

today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()

today_dir = os.path.join(BASE_INPUT_DIR, today)
yesterday_dir = os.path.join(BASE_INPUT_DIR, yesterday)

if os.path.exists(yesterday_dir):
    for f in os.listdir(yesterday_dir):
        if f.endswith(".mp4"):
            os.remove(os.path.join(yesterday_dir, f))
    try:
        os.rmdir(yesterday_dir)
    except OSError:
        pass

os.makedirs(today_dir, exist_ok=True)

if len(sys.argv) < 2:
    raise RuntimeError("Usage: python3 scripts/download.py <youtube_url>")

youtube_url = sys.argv[1]

subprocess.run([
    "yt-dlp",
    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "-o", os.path.join(today_dir, "%(title)s.%(ext)s"),
    youtube_url
], check=True)

log.info(f"Downloaded video from {youtube_url} into {today_dir}")