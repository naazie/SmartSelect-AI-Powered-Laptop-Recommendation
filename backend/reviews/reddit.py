# reddit.py
import praw
import json
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), 'reviews.env')
load_dotenv(dotenv_path)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ensure json_files folder exists
os.makedirs(os.path.join(BASE_DIR, "reviews", "json_files"), exist_ok=True)


# Reddit API setup
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)


def scrape_reddit_reviews(model_name, subreddit="laptops", limit=50):
    # 1. Prepare Paths & Query
    search_query = model_name.replace("_", " ") # Clean name for Reddit search
    if "review" not in search_query.lower():
        search_query += " review"
    
    cache_dir = os.path.join(BASE_DIR, "reviews", "json_files", "reddit_raw_reviews")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{model_name.replace(' ', '_')}.json")

    # 2. CACHE CHECK LOGIC (The Fix)
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            try:
                cached_reviews = json.load(f)
            except json.JSONDecodeError:
                cached_reviews = []
        
        # ONLY return if we actually have data. 
        # If list is empty, ignore cache and try scraping again.
        if cached_reviews and len(cached_reviews) > 0:
            print(f"♻️ Loading cached Reddit reviews from: {cache_path}")
            return cached_reviews
        else:
            print(f"⚠️ Empty cache found for {model_name}. Re-scraping with query: '{search_query}'")

    # 3. SCRAPE (If cache was missing or empty)
    reviews = []
    print(f"🕵️ Reddit Search Query: '{search_query}'")
    
    try:
        for submission in reddit.subreddit(subreddit).search(search_query, limit=limit):
            # Combine title and body
            text = f"{submission.title} {submission.selftext}"
            reviews.append(text)
            
            # Get comments (shallow)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                reviews.append(comment.body)
    except Exception as e:
        print(f"❌ Error connecting to Reddit: {e}")

    # 4. SAVE (Even if empty, to update timestamp, but next time it will retry thanks to logic above)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved {len(reviews)} Reddit reviews to: {cache_path}")
    return reviews

if __name__ == "__main__":
    model_name = "IdeaPad Slim 3"
    reviews = scrape_reddit_reviews(model_name)