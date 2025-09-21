import os
import re
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import DefaultCredentialsError

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    try:
        # build() will automatically use the credentials configured by gcloud
        # (Application Default Credentials) when no developerKey is provided.
        service_instance = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION)
        _youtube_service_state['instance'] = service_instance
        logging.info("YouTube service built successfully using Application Default Credentials.")
        return service_instance
    except DefaultCredentialsError:
        logging.error(
            "Authentication failed. Could not find Application Default Credentials. "
            "Please authenticate by running 'gcloud auth application-default login' "
            "or by setting the GOOGLE_APPLICATION_CREDENTIALS environment variable."
        )
        return None
    except HttpError as e:
        # This can happen if the API is not enabled for the project.
        logging.error(
            f"An HTTP error occurred building the YouTube service: {e}. "
            "Ensure the YouTube Data API v3 is enabled for your project."
        )
        return None
    except Exception as e:
        # Catch any other unexpected errors.
        logging.error(f"An unexpected error occurred while building YouTube service: {e}")
        # The instance remains None, and we won't check again.
        return None

def extract_video_id_from_url(url):
    """Extracts YouTube video ID from a URL using regex."""
    regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_details(video_ids):
    """
    Fetches details for a list of YouTube video IDs, handling batching for efficiency.
    The YouTube API v3 videos.list method can accept up to 50 IDs at once.
    """
    youtube = get_youtube_service()
    if not youtube or not video_ids:
        return []

    all_videos = []
    chunk_size = 50  # YouTube API limit for videos.list

    try:
        for i in range(0, len(video_ids), chunk_size):
            chunk = video_ids[i:i + chunk_size]
            
            response = youtube.videos().list(
                part='snippet,statistics',
                id=','.join(chunk)
            ).execute()

            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                thumbnails = snippet.get('thumbnails', {})
                # Prefer a higher quality thumbnail, but fall back to default.
                thumbnail_url = thumbnails.get('high', {}).get('url') or thumbnails.get('default', {}).get('url')
                all_videos.append({
                    'id': item.get('id'),
                    'title': snippet.get('title'),
                    'view_count': int(stats.get('viewCount', 0)),
                    'thumbnail_url': thumbnail_url,
                })
        return all_videos
    except HttpError as e:
        logging.error(f"An HTTP error {e.resp.status} occurred while fetching video details: {e.content}")
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
            thumbnails = snippet.get('thumbnails', {})
            # Prefer a higher quality thumbnail, but fall back to default.
            thumbnail_url = thumbnails.get('high', {}).get('url') or thumbnails.get('default', {}).get('url')
            videos.append({
                'id': item.get('id', {}).get('videoId'),
                'title': snippet.get('title'),
                'thumbnail_url': thumbnail_url,
                'channel_title': snippet.get('channelTitle'),
            })
        return videos
    except HttpError as e:
        logging.error(f"An HTTP error {e.resp.status} occurred while searching videos: {e.content}")
        return []