import yt_dlp # type: ignore
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound # type: ignore
import time

def get_playlist_transcripts(playlist_url):
    """
    Fetches and prints the title and transcript for each video in a YouTube playlist.
    """
    
    # Options for yt-dlp
    ydl_opts = {
        'extract_flat': True,  # Don't extract info for videos in playlist, just get list
        'quiet': True,         # Suppress yt-dlp's console output
        'no_warnings': True,
    }

    try:
        # Use yt-dlp to extract the playlist info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Safely extract playlist info
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            playlist_title = playlist_info.get('title', 'Unknown Playlist')
            print(f"Fetching videos from playlist: {playlist_title}\n")

            if 'entries' not in playlist_info or not playlist_info['entries']:
                print("Could not find any videos in the playlist.")
                return

            # Loop through each 'entry' (video) in the playlist
            for video in playlist_info['entries']:
                if not video:
                    continue
                    
                video_id = video.get('id')
                video_title = video.get('title', 'Unknown Title')
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                if not video_id:
                    continue
                
                # Print a clear separator and the video title
                print("\n" + "=" * 80)
                print(f"--- VIDEO TITLE: {video_title} ---")
                print(f"(Video URL: {video_url})")
                print("-" * 80)

                try:
                    # 1. List all available transcripts for the video (The method that should now work)
                    transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # 2. Find a transcript (will default to English or auto-generated English)
                    transcript = transcript_list_obj.find_transcript(['en'])
                    
                    # 3. Fetch the actual transcript data
                    transcript_data = transcript.fetch()
                    
                    # 4. Join all the 'text' parts from the transcript
                    full_transcript = " ".join([segment['text'] for segment in transcript_data])
                    
                    print(full_transcript)
                    
                    # Add a small delay to prevent being blocked for rapid requests
                    time.sleep(0.5) 

                except (TranscriptsDisabled, NoTranscriptFound):
                    print("!!! TRANSCRIPT NOT AVAILABLE: Transcripts are disabled or not found for this video.")
                except Exception as e:
                    # Catch any other remaining errors
                    print(f"!!! An error occurred while fetching transcript: {type(e).__name__}: {e}")

    except yt_dlp.utils.DownloadError as e:
        print(f"Error fetching playlist. Please check the URL: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__}: {e}")

    print("\n" + "=" * 80)
    print("Playlist processing complete.")

# --- Main execution ---
if __name__ == "__main__":
    url = input("Enter the YouTube Playlist URL: ")
    get_playlist_transcripts(url)