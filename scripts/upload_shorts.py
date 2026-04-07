import os
import glob
import pickle
import re
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLES_FILE = os.path.join(BASE_DIR, "titles.json")
print(f"📄 Using titles file at: {TITLES_FILE}")
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")

def get_youtube_client():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Refresh expired token if possible
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
            print("🔄 Refreshed expired access token")
        except Exception as e:
            print("⚠️ Token refresh failed, forcing re-authentication...")
            os.remove(TOKEN_FILE)
            creds = None

    # If no valid creds, run full OAuth flow
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("✅ New OAuth token generated")

    return build("youtube", "v3", credentials=creds)

def upload_short(youtube, video_path, title):
    description = f"{title}\n\n#shorts #viral #trending #gaming"
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:90],
                "description": description,
                "categoryId": "20"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"Uploaded: {video_path}")
    return response["id"]

def main():
    if not os.path.exists(TITLES_FILE):
        raise FileNotFoundError(f"titles.json not found at {TITLES_FILE}. Generate titles before uploading.")

    with open(TITLES_FILE, "r", encoding="utf-8") as f:
        titles = json.load(f)

    print(f"✅ Loaded {len(titles)} generated titles")

    # Normalize title keys to always include .mp4
    normalized_titles = {}
    for k, v in titles.items():
        if k.endswith(".mp4"):
            normalized_titles[k] = v
        else:
            normalized_titles[f"{k}.mp4"] = v

    titles = normalized_titles
    print(f"🔧 Normalized title keys: {list(titles.keys())}")

    shorts = sorted(f for f in glob.glob(os.path.join(BASE_DIR, "final_outputs", "*.mp4")))
    if not shorts:
        raise RuntimeError("No shorts found in final_outputs/, aborting upload")
    if len(shorts) < 5:
        print(f"⚠️ Only {len(shorts)} shorts found — uploading all available shorts")

    youtube = get_youtube_client()

    uploaded = []
    failed = []

    for short in shorts[:5]:
        name = os.path.basename(short)
        title = titles.get(name)

        if not title:
            print(f"⚠️ No title found for {name}, using fallback")
            title = os.path.splitext(name)[0].replace("_", " ").title()

        title = title.strip()

        # Ensure Shorts indicator is present
        if "#shorts" not in title.lower():
            title = f"{title} #Shorts"

        # Enforce YouTube title length limit (100 chars)
        title = title[:100]

        try:
            upload_short(youtube, short, title)
            uploaded.append(short)
        except Exception as e:
            print(f"❌ Upload failed for {short}: {e}")
            failed.append(short)

    # Only delete successfully uploaded files
    for short in uploaded:
        try:
            os.remove(short)
            print(f"🗑️ Deleted uploaded short: {short}")
        except Exception as e:
            print(f"⚠️ Could not delete {short}: {e}")

    if failed:
        print(f"⚠️ {len(failed)} shorts failed to upload and were kept locally")

if __name__ == "__main__":
    main()