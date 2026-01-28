import os
import json
import re
import concurrent.futures
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_comment_downloader import YoutubeCommentDownloader
from youtubesearchpython import VideosSearch

MODEL_NAME = "IdeaPad Slim 3"
NUM_VIDEOS = 3
import os
 
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ensure cache folder for all model reviews exists
cache_dir = os.path.join(BASE_DIR, "reviews", "json_files", "youtube_raw_reviews")

os.makedirs(cache_dir, exist_ok=True)

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def fetch_video_data(video):
    vid = video["id"]
    video_title = video["title"]

    print(f"📦 Processing video: {video_title}")

    transcript_text = ""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(vid)

        # Prefer manually created transcripts
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except NoTranscriptFound:
            # Fallback to automatically generated transcripts
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except NoTranscriptFound:
                print(f"🚫 No transcript available for video {video_title}")
                transcript = None

        if transcript:
            fetched = transcript.fetch()
            transcript_text = " ".join([t.text for t in fetched])
            print(f"✅ Transcript fetched for: {video_title} ({transcript.language_code})")

    except TranscriptsDisabled:
        print(f"❌ Transcripts are disabled for video {video_title}")
    except NoTranscriptFound:
        print(f"❌ No transcript found at all for video {video_title}")
    except Exception as e:
        print(f"⚠️ Error fetching transcript for video {video_title}: {e}")

    comments = []
    try:
        downloader = YoutubeCommentDownloader()
        for comment in downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={vid}', sort_by=0):
            text = comment['text']
            if len(text) > 10:
                comments.append(text)
        print(f"💬 {len(comments)} comments fetched for: {video_title}")
    except Exception as e:
        print(f"⚠️ Error fetching comments for {video_title}: {e}")

    combined_texts = [transcript_text] if transcript_text else []
    combined_texts.extend(comments)
    cleaned = [clean_text(r) for r in combined_texts if len(r.strip()) > 20]

    return cleaned

def scrape_youtube_reviews(model_name, num_videos=3):
    # Cache path for entire model's combined reviews
    cache_filepath = os.path.join(cache_dir, f"{model_name.replace(' ', '_')}.json")

    if "review" not in model_name.lower():
        model_name += " review"
    
    # Check if cached combined reviews exist
    if os.path.exists(cache_filepath):
        print(f"♻️ Loading cached combined reviews for model: {model_name}")
        with open(cache_filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    videos_search = VideosSearch(model_name, limit=num_videos)
    results = videos_search.result()["result"]

    all_reviews = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_videos) as executor:
        results_list = list(executor.map(fetch_video_data, results))
    for video_reviews in results_list:
        all_reviews.extend(video_reviews)

    # Save combined reviews into one JSON per model
    with open(cache_filepath, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    # print(f"💾 Saved combined reviews for {model_name} to {cache_filepath}")
    print(f"💾 Saved combined reviews for {model_name}")


    return all_reviews


if __name__ == "__main__":
    reviews = scrape_youtube_reviews(MODEL_NAME, NUM_VIDEOS)
