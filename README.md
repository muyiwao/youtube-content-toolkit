# YOUTUBE-CONTENT-TOOLKIT

This repository contains all the **scripts and core assets** used for automated content creation, data extraction, and video management for the channel.

---

## 🛠️ Content Management Structure

The repository maintains a clean separation between the working scripts (in the root) and the content files (in the folders).

### 📂 Content Folders

* **Long/**: Stores final processed assets (videos, cover art, metadata) for long-form content.
* **Shorts/**: Stores final processed assets (videos, cover art, metadata) for short-form content.
* **Utility/**: Contains any general-purpose helper scripts or temporary files.
    
    _Note: The video files (`.mp4`, `.jpg`, `.json`) are excluded from Git tracking via `.gitignore`._

### 🐍 Root Scripts

| Filename | Purpose | Dependencies |
| :--- | :--- | :--- |
| `extract_playlist_videos.py` | Extracts video URLs and metadata from YouTube playlists. | `yt-dlp` |
| `get_transcripts.py` | Extracts and processes transcripts for videos. | `yt-dlp`, `youtube-transcript-api` |
| `upload_to_youtube.py` | Handles the automated upload process for finished video files. | YouTube Data API (OAuth 2.0) |

---

## 🔐 Setup and Authentication

This project requires Python 3.11+ and the following specific configurations:

1.  **Dependencies:** Install required libraries: `pip install yt-dlp youtube-transcript-api google-api-python-client` (or similar).
2.  **Authentication:** The scripts rely on the YouTube Data API. The files `client_secret.json` and `token.pickle` are required for OAuth 2.0 authentication but are **ignored by Git** to protect credentials.