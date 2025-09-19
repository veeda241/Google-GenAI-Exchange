import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# A dictionary to hold the state of the YouTube service instance.
# 'checked' will be True after the first attempt to build the service.
# 'instance' will hold the service object or None.
_youtube_service_state = {'instance': None, 'checked': False}

def get_youtube_service():
    """
    Returns a YouTube service object, or None if API key is missing.
    Caches the result to avoid repeated checks and warnings.
    """
    global _youtube_service_state

    # If we've already checked, return the cached instance (which could be None).
    if _youtube_service_state['checked']:
        return _youtube_service_state['instance']

    # Mark that we are performing the check now.
    _youtube_service_state['checked'] = True

    # Read the API key from the environment. This happens only once.
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not API_KEY:
        print("Warning: YOUTUBE_API_KEY environment variable not set. YouTube features will be disabled.")
        # The instance remains None, and we won't check again.
        return None
    try:
        service_instance = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
        _youtube_service_state['instance'] = service_instance
        return service_instance
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        # The instance remains None, and we won't check again.
        return None

def extract_video_id_from_url(url):
    """Extracts YouTube video ID from a URL using regex."""
    regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_details(video_ids):
    """Fetches details for a list of YouTube video IDs."""
    youtube = get_youtube_service()
    if not youtube or not video_ids:
        return []

    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()

        videos = []
        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            videos.append({
                'id': item.get('id'),
                'title': snippet.get('title'),
                'view_count': stats.get('viewCount'),
            })
        return videos
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return []

def search_videos(query, max_results=6):
    """Searches for YouTube videos based on a query."""
    youtube = get_youtube_service()
    if not youtube:
        return []

    try:
        response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video',
            videoEmbeddable='true'
        ).execute()

        videos = []
        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            videos.append({
                'id': item.get('id', {}).get('videoId'),
                'title': snippet.get('title'),
            })
        return videos
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return []