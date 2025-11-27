from pytube import Playlist # type: ignore

def extract_youtube_playlist_videos(playlist_url):
    """
    Extracts and prints all video URLs from a YouTube playlist.

    Args:
        playlist_url (str): The URL of the YouTube playlist.

    Returns:
        list: A list of video URLs from the playlist.
    """
    try:
        # Initialize the Playlist object
        playlist = Playlist(playlist_url)
        
        print(f"\n📂 Playlist Title: {playlist.title}")
        print(f"📊 Total Videos Found: {len(playlist.video_urls)}\n")

        # Print and return all URLs
        for index, url in enumerate(playlist.video_urls, start=1):
            # print(f"{index}. {url}")
            print(f"{url}")


        return playlist.video_urls

    except Exception as e:
        print(f"❌ Error extracting playlist videos: {e}")
        return []

if __name__ == "__main__":
    # Example playlist URL
    playlist_url = input("Enter YouTube playlist URL: ").strip()
    extract_youtube_playlist_videos(playlist_url)
