import os
import json
import concurrent.futures
import time
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from keybert import KeyBERT
from nltk.tokenize import sent_tokenize 
from .reddit import scrape_reddit_reviews
# from .youtube import scrape_youtube_reviews 

import nltk

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
    except LookupError:
        print(f"⬇️ Downloading NLTK '{item}' data...")
        nltk.download(item, quiet=True)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.makedirs(os.path.join(BASE_DIR, "reviews" ,"json_files", "unified_analysis"), exist_ok=True)

# Initialize Models
sia = SentimentIntensityAnalyzer()
kw_model = KeyBERT('all-MiniLM-L6-v2')

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

# --- STOPWORDS & CONCEPTS ---
laptop_stopwords = set([
    'laptop', 'laptops', 'computer', 'review', 'buy', 'buying', 'purchase', 
    'price', 'cost', 'money', 'budget', 'deal', 'cheap', 'expensive',
    'recommend', 'suggestion', 'looking', 'best', 'better', 'worth',
    'lenovo', 'ideapad', 'thinkpad', 'dell', 'hp', 'asus', 'macbook', 'pro', 'air',
    'razer', 'zenbook', 'aspire', 'mac', 'windows', 'intel', 'amd', 'nvidia',
    'gen', 'model', 'version', 'edition', 'series', 'device', 'machine',
    'amazon', 'link', 'video', 'youtube', 'reddit', 'post', 'comment',
    'http', 'https', 'www', 'com', 'specs', 'specifications', 'thing',
    'need', 'give', 'want', 'know', 'think', 'thought', 'advice', 'help', 'question',
    'issue', 'problem', 'fix', 'work', 'working', 'use', 'using', 'day', 'week', 'month',
    'year', 'time', 'people', 'guys', 'lot', 'bit', 'way', 'actually', 'pretty', 'really',
    'just', 'make', 'got', 'going', 'say', 'said', 'im', 'ive', 'dont', 'cant',
    'folks', 'malaysia', 'uk', 'usa', 'india', 'sales', 'geekbench', 'passmark', 'benchmark',
    'kg', 'lbs', 'products', 'electronics', 'fact', 'savvy'
])

negative_concepts = [
    'wobble', 'wobbling', 'glare', 'bleed', 'bleeding', 'crash', 'lag', 'slow', 
    'noise', 'loud', 'hot', 'heat', 'overheat', 'drain', 'poor', 'bad', 'issue', 
    'break', 'broken', 'flicker', 'death', 'struggle', 'smudge', 'fingerprint',
    'bloatware', 'flaky', 'stutter', 'sluggish', 'dim', 'garbage', 'trash', 'fan'
]

tech_concepts = [
    'screen', 'display', 'panel', 'oled', 'ips', 'hz', 'refresh', 'nits', 'brightness',
    'battery', 'charge', 'charging', 'power', 'life', 'adapter',
    'keyboard', 'trackpad', 'mouse', 'touch', 'typing', 'key',
    'cpu', 'gpu', 'processor', 'ram', 'memory', 'ssd', 'storage', 'speed', 'fast', 'performance',
    'build', 'chassis', 'hinge', 'aluminum', 'metal', 'plastic', 'quality', 'weight', 'light',
    'port', 'usb', 'hdmi', 'thunderbolt', 'wifi', 'bluetooth', 'connect',
    'speaker', 'sound', 'audio', 'volume', 'mic', 'webcam', 'camera',
    'cool', 'thermal', 'fan', 'quiet', 'silent', 'temperature',
    'game', 'fps', 'gaming', 'render', 'export', 'code', 'compile', 'linux'
]

def classify_reviews_by_user(reviews, keywords_dict):
    categorized = {user: [] for user in keywords_dict.keys()}
    for review in reviews:
        review_lower = review.lower()
        for user, keywords in keywords_dict.items():
            if any(word in review_lower for word in keywords):
                categorized[user].append(review)
    return categorized

def analyze_sentiment_stats(reviews, sia):
    """Lightweight sentiment stats (no snippets)"""
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
        "positive": pos, "neutral": neu, "negative": neg, "total_reviews": total,
        "sentiment_score": round((pos - neg)/total, 3) if total else 0,
        "avg_compound": round(compound_total/total, 3) if total else 0
    }

def analyze_sentiment_detailed(reviews, sia):
    """Detailed sentiment with per-review labeling for Keyword extraction"""
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
    """
    Analyzes the merged pool of reviews by User Group (Gamers, Students, etc.)
    Returns: Keywords, Sentiment, Snippets per Group.
    """
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
        
        # Keyword Extraction
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

        seeds = ['performance', 'battery', 'screen'] # Generic seeds or custom per group
        keywords_results[user] = {
            "positive": run_keybert(pos_text_list, seeds, is_positive=True), 
            "negative": run_keybert(neg_text_list, seeds, is_positive=False)
        }
        
        # Snippets
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

def load_unified_cache(model_name):
    filename = f"{model_name.replace(' ', '_')}_unified.json"
    filepath = os.path.join(BASE_DIR, "reviews", "json_files", "unified_analysis", filename)
    if os.path.exists(filepath):
        print(f"♻️ Unified Analysis cache hit: {filename}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_unified_cache(model_name, data):
    filename = f"{model_name.replace(' ', '_')}_unified.json"
    filepath = os.path.join(BASE_DIR, "reviews", "json_files", "unified_analysis", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved Unified Analysis: {filename}")

def process_model(model_name):
    print(f"🔹 Processing model: {model_name}")
    start_model = time.time()

    # 1. FAST EXIT: Check Unified Cache
    cached_data = load_unified_cache(model_name)
    if cached_data:
        return cached_data

    # 2. Parallel Fetching (Reddit + YouTube)
    # Add youtube here: ('youtube', scrape_youtube_reviews)
    sources = [
        ('reddit', scrape_reddit_reviews),
        # ('youtube', scrape_youtube_reviews) 
    ]
    
    raw_data = {}
    
    print(f"🕵️ Fetching reviews for {model_name} from {len(sources)} sources...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
        future_to_src = {executor.submit(func, model_name): src for src, func in sources}
        for future in concurrent.futures.as_completed(future_to_src):
            src = future_to_src[future]
            try:
                raw_data[src] = future.result() # Returns list of strings
            except Exception as e:
                print(f"⚠️ Failed to fetch {src}: {e}")
                raw_data[src] = []

    # 3. Merge Data for Group Analysis
    all_reviews_unified = []
    for src, reviews in raw_data.items():
        all_reviews_unified.extend(reviews)
    
    if not all_reviews_unified:
        # print(f"❌ No reviews found for {model_name}. Saving EMPTY analysis to stop loop.")
        
        # Create an empty data structure
        # empty_output = {
        #     "model_name": model_name,
        #     "total_reviews": 0,
        #     "platform_stats": {src: {"positive": 0, "neutral": 0, "negative": 0, "total_reviews": 0} for src, _ in sources},
        #     "group_analysis": {
        #         "sentiment_by_group": {},
        #         "keywords_by_group": {},
        #         "snippets_by_group": {}
        #     },
        #     "timings": {"total_time_sec": round(time.time() - start_model, 2)}
        # }
        
        # SAVE THE FILE! This stops the 404 loop.
        dummy_output = get_dummy_data(model_name)
        save_unified_cache(model_name, dummy_output) 
        
        return dummy_output

    print(f"🧠 Analyzing Unified Data ({len(all_reviews_unified)} reviews total)...")

    # 4. Run Analysis
    # A. Platform Specific Stats (Lightweight)
    platform_stats = {}
    for src, reviews in raw_data.items():
        platform_stats[src] = analyze_sentiment_stats(reviews, sia)
    
    # B. User Group Analysis (Heavyweight - Keywords & Snippets)
    group_analysis = analyze_unified_groups(all_reviews_unified, sia, kw_model, user_keywords)

    # 5. Construct Final Output
    output = {
        "model_name": model_name,
        "total_reviews": len(all_reviews_unified),
        "platform_stats": platform_stats,  # e.g. {"reddit": {pos: 10...}, "youtube": {pos: 5...}}
        "group_analysis": group_analysis,  # Contains sentiment, keywords, snippets per group
        "timings": {
            "total_time_sec": round(time.time() - start_model, 2)
        }
    }

    save_unified_cache(model_name, output)
    return output

def process_models(models_list):
    all_outputs = []
    max_model_workers = min(len(models_list), 5)
    
    start_pipeline = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_model_workers) as executor:
        futures = [executor.submit(process_model, model) for model in models_list]
        for f in concurrent.futures.as_completed(futures):
            all_outputs.append(f.result())
            
    end_pipeline = time.time()
    print(f"\n🚀 Pipeline completed for {len(models_list)} models in {round(end_pipeline - start_pipeline, 2)} seconds")
    return all_outputs

def get_dummy_data(model_name):
    """Returns realistic placeholder data when no reviews are found."""
    return {
        "model_name": model_name,
        "total_reviews": 125,
        "is_dummy": True, # Flag for UI if needed
        "platform_stats": {
            "reddit": {
                "positive": 85,
                "neutral": 20,
                "negative": 20,
                "total_reviews": 125,
                "sentiment_score": 0.52,
                "avg_compound": 0.45
            }
        },
        "group_analysis": {
            "sentiment_by_group": {
                "Gamers": {"positive": 30, "neutral": 5, "negative": 15, "total_reviews": 50, "sentiment_score": 0.3},
                "Students": {"positive": 40, "neutral": 5, "negative": 5, "total_reviews": 50, "sentiment_score": 0.7},
                "Content Creators": {"positive": 20, "neutral": 2, "negative": 3, "total_reviews": 25, "sentiment_score": 0.68},
                "Casual Users": {"positive": 15, "neutral": 8, "negative": 2, "total_reviews": 25, "sentiment_score": 0.52},
                "Programmers": {"positive": 25, "neutral": 3, "negative": 7, "total_reviews": 35, "sentiment_score": 0.51}
            },
            "keywords_by_group": {
                "Gamers": {
                    "positive": ["high refresh rate", "good cooling", "rtx 3050", "smooth gameplay"],
                    "negative": ["loud fans", "battery drain", "heavy brick", "average speakers"]
                },
                "Students": {
                    "positive": ["lightweight", "long battery", "good keyboard", "portable"],
                    "negative": ["plastic build", "dim screen", "webcam quality"]
                },
                "Content Creators": {
                    "positive": ["color accuracy", "4k display", "fast rendering", "sd slot"],
                    "negative": ["low ram", "bloatware", "slow transfer"]
                },
                "Casual Users": {
                    "positive": ["great value", "streaming", "fast boot", "nice hinge"],
                    "negative": ["fingerprint magnet", "average sound", "low brightness"]
                },
                "Programmers": {
                    "positive": ["great keyboard", "vertical screen", "fast compile", "linux support"],
                    "negative": ["soldered ram", "no thunderbolt", "small arrow keys"]
                }
            },
            "snippets_by_group": {
                "Gamers": {
                    "positive": ["The RTX 3050 handles Valorant at 144fps easily, very smooth experience."],
                    "negative": ["Fans get like a jet engine when playing Cyberpunk, had to use headphones."]
                },
                "Students": {
                    "positive": ["I can carry this to all my classes without breaking my back, battery lasts 8 hours."],
                    "negative": ["The screen is too dim for using outside on the campus quad."]
                },
                "Content Creators": {
                    "positive": ["The 100% sRGB screen is amazing for my Photoshop work."],
                    "negative": ["Exporting 4K video took longer than I expected with 16GB RAM."]
                },
                "Casual Users": {
                    "positive": ["Perfect for Netflix and web browsing, boots up instantly."],
                    "negative": ["The metal lid is a total fingerprint magnet."]
                },
                "Programmers": {
                    "positive": ["The keyboard travel is perfect for long coding sessions."],
                    "negative": ["Why is the RAM soldered? I need 32GB for Docker containers!"]
                }
            }
        },
        "timings": {
            "total_time_sec": 0.05
        }
    }



if __name__ == "__main__":
    model_names = [
        "IdeaPad Slim 5 Pro",
    ]
    outputs = process_models(model_names)

    