import os
import json
import time
import re
import sys
import asyncio
import nltk

# --- 1. SETUP PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir) # No longer needed since we mock the scraper locally

# --- REMOVED REAL SCRAPER IMPORT ---
# from reddit import scrape_reddit_reviews 

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from keybert import KeyBERT
from nltk.tokenize import sent_tokenize 

# --- 2. ROBUST NLTK LOADER ---
required_nltk = ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'vader_lexicon']
for item in required_nltk:
    try:
        if item == 'vader_lexicon': 
            nltk.data.find('sentiment/vader_lexicon.zip')
        elif item == 'averaged_perceptron_tagger': 
            nltk.data.find('taggers/averaged_perceptron_tagger')
        elif item == 'punkt_tab': 
            nltk.data.find('tokenizers/punkt_tab')
        else: 
            nltk.data.find(f'tokenizers/{item}')
    except (LookupError, OSError):
        # print(f"⬇️ Downloading NLTK '{item}' data...")
        nltk.download(item, quiet=True)

# --- 3. DIRECTORY SETUP ---
BASE_DIR = current_dir
os.makedirs(os.path.join(BASE_DIR, "json_files", "unified_analysis"), exist_ok=True)

# --- 4. MODEL INITIALIZATION ---
sia = SentimentIntensityAnalyzer()
kw_model = KeyBERT('all-MiniLM-L6-v2')

# --- 5. DATA CLEANING & CONSTANTS ---
def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = text.replace("/", " ").replace("\\", " ")
    text = re.sub(r"\s+", " ", text) 
    return text.strip()

user_keywords = {
    'Gamers': ['fps', 'game', 'gaming', 'gpu', 'twitch', 'stream', 'fortnite', 'csgo', 'valorant', 'esports', 'high refresh rate', 'overclock', 'mmorpg', 'low latency', 'ray tracing'],
    'Students': ['study', 'school', 'college', 'assignment', 'homework', 'lecture', 'project', 'exam', 'class', 'research', 'zoom', 'online class', 'notes', 'presentation', 'group work', 'pdf', 'writing', 'report'],
    'Content Creators': ['youtube', 'editing', 'video', 'render', 'streaming', 'photoshop', 'premiere', 'vlog', 'after effects', 'color grading', 'audio mixing', 'graphic tablet', '1080p', '4k', 'animation', 'creative cloud'],
    'Casual Users': ['internet', 'browsing', 'movies', 'netflix', 'social media', 'web', 'youtube', 'watching', 'facebook', 'instagram', 'twitter', 'spotify', 'podcast', 'email', 'shopping'],
    'Programmers / Engineers': ['coding', 'programming', 'python', 'java', 'software', 'developer', 'debug', 'compile', 'engineer', 'data', 'linux', 'git', 'docker', 'algorithm', 'machine learning', 'api', 'script']
}

laptop_stopwords = set(['laptop', 'laptops', 'computer', 'review', 'buy', 'buying', 'purchase', 'price', 'cost', 'money', 'budget', 'deal', 'cheap', 'expensive', 'recommend', 'suggestion', 'looking', 'best', 'better', 'worth', 'lenovo', 'ideapad', 'thinkpad', 'dell', 'hp', 'asus', 'macbook', 'pro', 'air', 'razer', 'zenbook', 'aspire', 'mac', 'windows', 'intel', 'amd', 'nvidia', 'gen', 'model', 'version', 'edition', 'series', 'device', 'machine', 'amazon', 'link', 'video', 'youtube', 'reddit', 'post', 'comment', 'http', 'https', 'www', 'com', 'specs', 'specifications', 'thing', 'need', 'give', 'want', 'know', 'think', 'thought', 'advice', 'help', 'question', 'issue', 'problem', 'fix', 'work', 'working', 'use', 'using', 'day', 'week', 'month', 'year', 'time', 'people', 'guys', 'lot', 'bit', 'way', 'actually', 'pretty', 'really', 'just', 'make', 'got', 'going', 'say', 'said', 'im', 'ive', 'dont', 'cant', 'folks', 'malaysia', 'uk', 'usa', 'india', 'sales', 'geekbench', 'passmark', 'benchmark', 'kg', 'lbs', 'products', 'electronics', 'fact', 'savvy'])

negative_concepts = ['wobble', 'wobbling', 'glare', 'bleed', 'bleeding', 'crash', 'lag', 'slow', 'noise', 'loud', 'hot', 'heat', 'overheat', 'drain', 'poor', 'bad', 'issue', 'break', 'broken', 'flicker', 'death', 'struggle', 'smudge', 'fingerprint', 'bloatware', 'flaky', 'stutter', 'sluggish', 'dim', 'garbage', 'trash', 'fan']

tech_concepts = ['screen', 'display', 'panel', 'oled', 'ips', 'hz', 'refresh', 'nits', 'brightness', 'battery', 'charge', 'charging', 'power', 'life', 'adapter', 'keyboard', 'trackpad', 'mouse', 'touch', 'typing', 'key', 'cpu', 'gpu', 'processor', 'ram', 'memory', 'ssd', 'storage', 'speed', 'fast', 'performance', 'build', 'chassis', 'hinge', 'aluminum', 'metal', 'plastic', 'quality', 'weight', 'light', 'port', 'usb', 'hdmi', 'thunderbolt', 'wifi', 'bluetooth', 'connect', 'speaker', 'sound', 'audio', 'volume', 'mic', 'webcam', 'camera', 'cool', 'thermal', 'fan', 'quiet', 'silent', 'temperature', 'game', 'fps', 'gaming', 'render', 'export', 'code', 'compile', 'linux']

# --- 6. MOCKED SCRAPER (BYPASS REDDIT API) ---

async def scrape_reddit_reviews_mock(model_name):
    """
    Returns a predetermined list of realistic-looking reviews instantly.
    Simulates scraping 50+ reviews without hitting the network.
    """
    print(f" Reddit Scrape for: {model_name}")
    await asyncio.sleep(0.1) # Simulate tiny network latency
    
    base_reviews = [
        f"I bought the {model_name} last week. The screen is amazing, very bright and color accurate. Battery lasts about 8 hours for web browsing.",
        "Terrible experience with this laptop. The fans are super loud even when idle, and it gets hot fast.",
        "Best budget laptop I've ever owned. Keyboard feels nice to type on, trackpad is decent. Performance is great for coding.",
        "Beware of the hinge issue! Mine broke after 6 months of careful use. Lenovo support was unhelpful.",
        "Gaming performance is solid. I get 144fps in Valorant and 60fps in Cyberpunk on medium settings.",
        "The build quality feels premium, all aluminum chassis. But the webcam is potato quality, 720p in 2024 is a joke.",
        "Perfect for students. Lightweight, good battery life, fits easily in my backpack. Handles Zoom calls and multiple tabs fine.",
        "Bloatware is insane on this machine. Had to do a fresh install of Windows to get rid of McAfee and other junk.",
        "The OLED screen is gorgeous but I'm worried about burn-in. Blacks are perfect though.",
        "Wifi card is flaky. Keeps disconnecting randomly. Replaced it with an Intel AX210 and it works fine now."
    ]
    
    # Multiply to simulate volume (50 reviews)
    return base_reviews * 5

# --- 7. HELPER FUNCTIONS ---

def classify_reviews_by_user(reviews, keywords_dict):
    categorized = {user: [] for user in keywords_dict.keys()}
    for review in reviews:
        review_lower = review.lower()
        for user, keywords in keywords_dict.items():
            if any(word in review_lower for word in keywords):
                categorized[user].append(review)
    return categorized

def analyze_sentiment_stats(reviews, sia):
    pos = neg = neu = 0
    compound_total = 0
    for r in reviews:
        score = sia.polarity_scores(r)
        compound = score['compound']
        compound_total += compound
        if compound >= 0.05: pos += 1
        elif compound <= -0.05: neg += 1
        else: neu += 1
    
    total = len(reviews)
    return {
        "positive": pos, "neutral": neu, "negative": neg, 
        "total_reviews": total,
        "sentiment_score": round((pos - neg)/total, 3) if total else 0,
        "avg_compound": round(compound_total/total, 3) if total else 0
    }

def analyze_sentiment_detailed(reviews, sia):
    agg = analyze_sentiment_stats(reviews, sia)
    per_review = []
    for r in reviews:
        score = sia.polarity_scores(r)['compound']
        label = "positive" if score >= 0.05 else "negative" if score <= -0.05 else "neutral"
        per_review.append({"text": r, "label": label, "score": score})
    return agg, per_review

def filter_keywords(candidates, is_positive_bucket=False):
    filtered = []
    for kw, score in candidates:
        kw_clean = re.sub(r"[^a-zA-Z0-9\s]", "", kw).strip()
        words = kw_clean.lower().split()
        if not words: continue

        if words[0] in laptop_stopwords or words[-1] in laptop_stopwords: continue
        
        if is_positive_bucket:
            if any(bad_word in kw_clean for bad_word in negative_concepts): continue
            if not any(tech in kw_clean for tech in tech_concepts): continue 
            kw_score = sia.polarity_scores(kw_clean)['compound']
            if kw_score < -0.05: continue

        try:
            tags = nltk.pos_tag(words)
            has_noun = any(tag.startswith('N') for word, tag in tags)
            if not has_noun: continue
        except: pass

        filtered.append(kw_clean)
    return list(dict.fromkeys(filtered))[:5]

def analyze_unified_groups(all_reviews, sia, kw_model, user_keywords):
    clean_reviews = [clean_text(r) for r in all_reviews if len(r.strip()) > 20]
    user_categorized = classify_reviews_by_user(clean_reviews, user_keywords)
    
    sentiment_results = {}
    keywords_results = {}
    example_snippets = {}

    for user in user_keywords.keys():
        user_reviews = user_categorized.get(user, [])
        agg, per_review = analyze_sentiment_detailed(user_reviews, sia)
        
        pos_text_list = [r["text"] for r in per_review if r["label"] == "positive"]
        neg_text_list = [r["text"] for r in per_review if r["label"] == "negative"]
        
        def run_keybert(text_list, seeds, is_positive=False):
            if not text_list: return []
            text_blob = " ".join(text_list)
            current_seeds = tech_concepts if is_positive else seeds
            candidates = kw_model.extract_keywords(
                text_blob, keyphrase_ngram_range=(1, 2), stop_words='english',
                use_maxsum=False, use_mmr=True, diversity=0.7, top_n=20, 
                seed_keywords=current_seeds
            )
            return filter_keywords(candidates, is_positive_bucket=is_positive)

        seeds = ['performance', 'battery', 'screen']
        keywords_results[user] = {
            "positive": run_keybert(pos_text_list, seeds, is_positive=True), 
            "negative": run_keybert(neg_text_list, seeds, is_positive=False)
        }
        
        all_sentences = []
        for review in user_reviews:
            clean_rev = re.sub(r"\*\*.*?\*\*", "", review).replace("x200B", "")
            sentences = sent_tokenize(clean_rev) 
            all_sentences.extend(sentences)

        scored_sentences = []
        for sent in all_sentences:
            clean_sent = sent.strip()
            if 20 < len(clean_sent) < 300: 
                score = sia.polarity_scores(clean_sent)['compound']
                scored_sentences.append((score, clean_sent))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        pos_snips = [s[1] for s in scored_sentences if s[0] > 0.6][:3]
        
        scored_sentences.sort(key=lambda x: x[0])
        neg_snips = [s[1] for s in scored_sentences if s[0] < -0.4][:3]

        example_snippets[user] = {"positive": pos_snips, "negative": neg_snips}
        sentiment_results[user] = agg

    return {
        "sentiment_by_group": sentiment_results,
        "keywords_by_group": keywords_results,
        "snippets_by_group": example_snippets
    }

# --- 8. HELPER WRAPPER ---
def analyze_platform_stats_wrapper(raw_data):
    stats = {}
    for src, reviews in raw_data.items():
        stats[src] = analyze_sentiment_stats(reviews, sia)
    return stats

# --- 9. PROCESSOR (Uses Mock Scraper) ---

async def process_model(model_name):
    await asyncio.sleep(5)
    print(f"🔹 Processing model: {model_name} ")
    start_model = time.time()

    # NOTE: Cache check removed so we ALWAYS re-process (good for load testing CPU)
    # If you want cache, add the load_unified_cache check back here.

    # 1. FETCH (Using Mock)
    raw_data = {}
    # Directly call the mock function
    reddit_reviews = await scrape_reddit_reviews_mock(model_name)
    raw_data['reddit'] = reddit_reviews

    # 3. MERGE
    all_reviews_unified = []
    for src, reviews in raw_data.items():
        all_reviews_unified.extend(reviews)

    print(f"🧠 Analyzing Unified Data ({len(all_reviews_unified)} reviews total)...")

    # 5. RUN ANALYSIS
    # The expensive part (KeyBERT, VADER) runs for real on the dummy text
    platform_stats = await asyncio.to_thread(analyze_platform_stats_wrapper, raw_data)
    group_analysis = await asyncio.to_thread(analyze_unified_groups, all_reviews_unified, sia, kw_model, user_keywords)

    # 6. OUTPUT
    output = {
        "model_name": model_name,
        "total_reviews": len(all_reviews_unified),
        "platform_stats": platform_stats,
        "group_analysis": group_analysis,
        "timings": {
            "total_time_sec": round(time.time() - start_model, 2)
        }
    }

    # No need to save cache for load testing, but you can if you want
    # save_unified_cache(model_name, output)
    return output

async def process_models_without_cache(models_list):
    
    if isinstance(models_list, str): 
        models_list = [models_list]
    
    results = []
    for model in models_list:
        res = await process_model(model)
        results.append(res)
    return results

if __name__ == "__main__":
    asyncio.run(process_models_without_cache(["IdeaPad Slim 5 Pro"]))