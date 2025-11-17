import os
import re
import json
import pickle
import time
import unicodedata
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ------------------------------------------
# CONFIGURATION
# ------------------------------------------
ROOT_PATH = r"C:\Project_Works\youtube-content-toolkit"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = os.path.join(ROOT_PATH, "client_secret.json")
TOKEN_FILE = os.path.join(ROOT_PATH, "token.pickle")

# ------------------------------------------
# AUTHENTICATION
# ------------------------------------------
def get_authenticated_service():
    creds = None

    # Load local token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials → force login
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                # Try refresh normally
                creds.refresh(Request())
            else:
                # Force new login
                raise Exception("Force OAuth Re-login")

        except Exception:
            print("🔐 Performing fresh Google OAuth login...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Store the new token
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


# ------------------------------------------
# TEXT CLEANING UTILITIES
# ------------------------------------------
def clean_text(text: str) -> str:
    """Remove problematic characters and normalize for YouTube-safe upload."""
    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "−": "-",
        "–": "-",
        "°": " degrees",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"'
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Remove LaTeX, Markdown, and hidden control chars
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\\\", "", text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)  # Remove hidden control characters
    text = re.sub(r"[\u2028\u2029]", " ", text)  # Line/paragraph separators
    text = re.sub(r"\s+", " ", text).strip()

    # Remove unsafe symbols < > & which may break API JSON encoding
    text = text.replace("<", "").replace(">", "").replace("&", "and")

    if len(text) > 4900:
        text = text[:4895] + "..."
    return text


def clean_tags(tag_list):
    """Sanitize YouTube tags to prevent 400 invalidTags error."""
    if not tag_list:
        return None
    cleaned = []
    for tag in tag_list:
        tag = unicodedata.normalize("NFKD", tag).encode("ascii", "ignore").decode("ascii")
        tag = re.sub(r"[^A-Za-z0-9\s]", "", tag)
        tag = re.sub(r"\s+", " ", tag).strip()
        if 2 <= len(tag) <= 30:
            cleaned.append(tag)
    return list(dict.fromkeys(cleaned)) if cleaned else None

# ------------------------------------------
# UPLOAD FUNCTION
# ------------------------------------------
def upload_video(youtube, video_file, metadata_file, thumbnail_file=None):
    """Uploads a single video to YouTube with full sanitization and auto-fallback."""
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    title = clean_text(metadata.get("title", os.path.basename(video_file)))
    description = clean_text(metadata.get("description", ""))
    raw_tags = metadata.get("tags", [])
    tags = clean_tags(raw_tags)

    if tags and sum(len(t) for t in tags) > 450:
        tags = tags[:8]

    privacy = metadata.get("privacyStatus", "public")
    category_id = metadata.get("categoryId", "27")

    print(f"\n📤 Uploading: {title}")
    print(f"🧹 Final tags before upload: {tags}")

    request_body = {
        "snippet": {"title": title, "description": description, "categoryId": category_id},
        "status": {"privacyStatus": privacy},
    }
    if tags:
        request_body["snippet"]["tags"] = tags

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        try:
            _, response = upload_request.next_chunk()
            if response and "id" in response:
                video_id = response["id"]
                print(f"✅ Uploaded successfully: https://www.youtube.com/watch?v={video_id}")

                if thumbnail_file and os.path.exists(thumbnail_file):
                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_file)
                    ).execute()
                    print("📸 Thumbnail set successfully.")
            else:
                print("❌ Upload incomplete or failed.")
        except HttpError as e:
            error_message = str(e)
            print(f"⚠️ Upload failed: {error_message}")

            # --- Handle Invalid Tags ---
            if "invalidTags" in error_message or "invalid video keywords" in error_message:
                print("🚫 Tags rejected by YouTube — retrying without tags...")
                if "tags" in request_body["snippet"]:
                    del request_body["snippet"]["tags"]
                upload_request = youtube.videos().insert(
                    part="snippet,status",
                    body=request_body,
                    media_body=media
                )
                _, response = upload_request.next_chunk()
                if response and "id" in response:
                    print(f"✅ Uploaded successfully (no tags): https://www.youtube.com/watch?v={response['id']}")
                else:
                    raise

            # --- Handle Invalid Description ---
            elif "invalidDescription" in error_message or "invalid video description" in error_message:
                print("🚫 Description rejected by YouTube — retrying with minimal safe text...")
                request_body["snippet"]["description"] = "Watch this educational video."
                upload_request = youtube.videos().insert(
                    part="snippet,status",
                    body=request_body,
                    media_body=media
                )
                _, response = upload_request.next_chunk()
                if response and "id" in response:
                    print(f"✅ Uploaded successfully (safe description): https://www.youtube.com/watch?v={response['id']}")
                else:
                    raise

            elif e.resp.status in [403, 500, 503]:
                print("⏳ Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise

# ------------------------------------------
# SCAN AND UPLOAD ALL
# ------------------------------------------
def upload_all_videos():
    youtube = get_authenticated_service()
    for category in ["Long", "Shorts"]:
        category_path = os.path.join(ROOT_PATH, category)
        if not os.path.exists(category_path):
            continue
        for outer_folder in os.listdir(category_path):
            outer_folder_path = os.path.join(category_path, outer_folder)
            if not os.path.isdir(outer_folder_path):
                continue
            for inner_folder in os.listdir(outer_folder_path):
                inner_folder_path = os.path.join(outer_folder_path, inner_folder)
                if not os.path.isdir(inner_folder_path):
                    continue
                video_file = next((os.path.join(inner_folder_path, f)
                                  for f in os.listdir(inner_folder_path) if f.endswith(".mp4")), None)
                metadata_file = next((os.path.join(inner_folder_path, f)
                                     for f in os.listdir(inner_folder_path) if f.endswith(".json")), None)
                thumbnail_file = next((os.path.join(inner_folder_path, f)
                                      for f in os.listdir(inner_folder_path) if f.endswith(".jpg")), None)
                if video_file and metadata_file:
                    upload_video(youtube, video_file, metadata_file, thumbnail_file)
                    print(f"📂 Processed: {video_file}")
                else:
                    print(f"⚠️ Missing files in {inner_folder_path}")

# ------------------------------------------
# MAIN EXECUTION
# ------------------------------------------
if __name__ == "__main__":
    upload_all_videos()
