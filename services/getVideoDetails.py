import os
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from utils import format_timestamp,groupTranscript

load_dotenv()


def extract_video_id(video_url):
    if not video_url:
        return None
    url_or_id = video_url.strip()
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    pattern = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url_or_id)
    return match.group(1) if match else None


# https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=API_KEY
def getTitle(video_id):
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                return data["items"][0]["snippet"]["title"]
        except Exception:
            pass

    # Fallback to YouTube oEmbed API (no API key required)
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        res = requests.get(oembed_url, timeout=5)
        if res.status_code == 200:
            oembed_data = res.json()
            if "title" in oembed_data:
                return oembed_data["title"]
    except Exception:
        pass

    return "Unknown Title"

    

def fetch_video_transcript(video_id):
    ytt = YouTubeTranscriptApi()
    transcript_list = ytt.list(video_id)
    
    preferred_languages = ['en', 'en-US', 'en-GB', 'en-CA', 'en-IN', 'en-AU', 'en-NZ']
    
    # 1. Try preferred English language codes
    try:
        transcript = transcript_list.find_transcript(preferred_languages)
        return transcript.fetch()
    except Exception:
        pass
        
    # 2. Try any transcript whose language_code starts with 'en'
    for t in transcript_list:
        if t.language_code.startswith('en'):
            try:
                return t.fetch()
            except Exception:
                pass

    # 3. Try to translate any translatable transcript to English
    for t in transcript_list:
        if t.is_translatable:
            try:
                return t.translate('en').fetch()
            except Exception:
                pass

    # 4. Fallback: Take the first available transcript in original language
    for t in transcript_list:
        try:
            return t.fetch()
        except Exception:
            pass

    # 5. Fallback to direct fetch
    return ytt.fetch(video_id)


def getVideoDetails(video_url):
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL or Video ID"}

        fetched_transcript = fetch_video_transcript(video_id)
        if hasattr(fetched_transcript, "to_raw_data"):
            transcript = fetched_transcript.to_raw_data()
        else:
            transcript = fetched_transcript

        grouped_transcript = groupTranscript(transcript, 30)

        formatted_transcript = []
        transcript_text_parts = []

        for entry in grouped_transcript:
            transcript_text_parts.append(entry["text"])
            formatted_transcript.append({
                "timestamp": format_timestamp(entry["start"]),
                "text": entry["text"]
            })

        transcript_text = " ".join(transcript_text_parts)
        title = getTitle(video_id)
        if isinstance(title, dict) and "error" in title:
            return {"error": title["error"]}
    
        return {
            "title": title,
            "transcript_text": transcript_text,
            "formatted_transcript": formatted_transcript
        }
    except Exception as e:
        return {"error": str(e)}

