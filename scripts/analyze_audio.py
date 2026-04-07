import subprocess
import json
import os

INPUT_VIDEO = "input_videos/CRAZIEST GAME! GEN.G vs VERREL - HIGHLIGHTS ｜ VCT 2026： Pacific Kickoff.mp4"
TEMP_AUDIO = "temp_audio.wav"

INTRO_SKIP = 60
OUTRO_SKIP = 60
CLIP_LENGTH = 30
NUM_CLIPS = 5


def extract_audio():
    subprocess.run([
        "ffmpeg", "-y",
        "-i", INPUT_VIDEO,
        "-ac", "1",
        "-ar", "16000",
        TEMP_AUDIO
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def detect_peaks():
    cmd = [
        "ffmpeg",
        "-i", TEMP_AUDIO,
        "-af", "silencedetect=noise=-30dB:d=0.4",
        "-f", "null", "-"
    ]

    result = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        text=True
    )

    times = []
    for line in result.stderr.split("\n"):
        if "silence_end" in line:
            t = float(line.split("silence_end: ")[1].split(" |")[0])
            times.append(t)

    return times


def select_clips(times, duration):
    valid = [
        t for t in times
        if INTRO_SKIP < t < (duration - OUTRO_SKIP - CLIP_LENGTH)
    ]

    step = max(1, len(valid) // NUM_CLIPS)
    return valid[::step][:NUM_CLIPS]


def get_duration():
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1",
         INPUT_VIDEO],
        stdout=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())


if __name__ == "__main__":
    extract_audio()
    duration = get_duration()
    peaks = detect_peaks()
    clips = select_clips(peaks, duration)

    with open("clip_times.json", "w") as f:
        json.dump(clips, f, indent=2)

    os.remove(TEMP_AUDIO)

    print("✅ Peak timestamps saved:", clips)