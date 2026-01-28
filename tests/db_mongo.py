from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np
from passlib.context import CryptContext
# from Laptop_Bot import fetch_laptop_details

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "keyword_processor_db")

if not MONGO_URI:
    raise Exception("MONGO_URI not set. Check your .env file and ensure dotenv is installed.")


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
requests_collection = db["requests"]
laptops_collection = db["laptops"]
users_collection = db["users"]

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto") 

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(username, password):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists"
    
    hashed_pass = hash_password(password)
    user_data = {
        "username": username,
        "password": hashed_pass,
        "created_at": datetime.now(),
        "recommended": [], # Initialize recommended list
        "wishlist": []     # Initialize wishlist list
    }
    result = users_collection.insert_one(user_data)
    return True, str(result.inserted_id)

def get_user_by_username(username):
    user = users_collection.find_one({"username": username})
    return user

def store_initial_request(ip, keyword):
    request_data = { 
        "ip_address": ip,
        "keyword": keyword,
        "timestamp": datetime.now(),
        "bot_result": None,
        "status": "pending"
    }
    result = requests_collection.insert_one(request_data)
    return str(result.inserted_id) 

def store_bot_response(request_id_str, bot_result):
    """Updates the request document with the bot's result."""
    requests_collection.update_one(
        {"_id": ObjectId(request_id_str)},
        {"$set": {"bot_result": bot_result, "status": "processed"}}
    )

# MODIFIED: Added user_id to the function signature
def store_laptop_recommendations(request_id, items, query_str, user_id=None):
    from Laptop_Bot import fetch_laptop_details  # local import avoids circular dependency
    # ['6929e58cab0f9dc5f99263d8', [{'model': 'Lenovo Legion Slim 5', 'price_inr': '₹1,35,000', 'why': 'Offers great gaming power with a strong processor and graphics card, making it ideal for your demanding tasks and entertainment.'}, {'model': 'Lenovo Yoga Slim 7 Pro', 'price_inr': '₹1,30,000', 'why': 'This laptop delivers a premium experience with its stunning display and smooth performance, perfect for both work and media consumption.'}, {'model': 'Lenovo ThinkBook 16p Gen 3', 'price_inr': '₹1,40,000', 'why': 'Built for professionals, it boasts powerful specs for seamless multitasking and a vibrant screen for an enjoyable viewing experience.'}, {'model': 'Lenovo IdeaPad Pro 5', 'price_inr': '₹1,32,000', 'why': 'Its balance of performance and display quality makes it excellent for everyday use, creative work, and watching movies with clarity.'}, {'model': 'Lenovo Legion 5 Pro', 'price_inr': '₹1,38,000', 'why': 'This powerful machine excels in gaming and video editing, offering a top-notch visual experience for all your high-demand needs.'}], 'use_case: For everyday tasks (browsing, movies, office work) ; budget: Above ₹1,30,000 (Premium laptops) ; processor: Medium – for smooth multitasking (Intel i5 / Ryzen 5) ; ram: 16GB (Best for multitasking and coding) ; gpu: Yes, for gaming, video editing, or graphics-heavy work ; screen_size: Standard (15–16 inches, balanced size) ; battery: Average battery is fine (5–7 hours) ; weight: Doesn’t matter to me ; priorities: Fast performance, Good display quality, Long battery life, Lightweight and portable', '68fa16f36eecfbbfabf1e043']
    

    new_models = []
    item_map = {}

    # Step 1: Identify models that are not in DB
    for item in items:
        doc = item.copy()
        model = doc.get("model")

        if not model:
            print("Skipping item without model key")
            continue

        item_map[model] = doc
        existing = laptops_collection.find_one({"model": model})
        print(f"Checking model in DB: {model} - Found: {bool(existing)}")
        if not existing:
            new_models.append({"model": model})
            print(f"Marked for detail fetch: {model}")

    # Step 2: Fetch details for new models (batch request)
    fetched_details = []
    if new_models:
        print(f"\nFetching details for {len(new_models)} new models...")
        try:
            fetched_details = fetch_laptop_details(new_models, return_json=True)
            # print(f"Fetched details for {fetched_details} models.")
            if not isinstance(fetched_details, list):
                print("⚠️ fetch_laptop_details did not return a list — wrapping result manually.")
                fetched_details = [fetched_details]
        except Exception as e:
            print(f"Error fetching laptop details: {e}")
    else:
        print("No new models to fetch.\n")

    # Step 3: Build a mapping from model → detailed specs
    fetched_map = {}
    for detail in fetched_details or []:
        model_name = detail.get("model")
        if model_name:
            fetched_map[model_name] = detail
            print(f"Mapped fetched details for model: {detail}")

    # Step 4: Merge fetched specs and upsert into DB
    added, updated = 0, 0

    for model, doc in item_map.items():
        existing = laptops_collection.find_one({"model": model})
        print(f"\nProcessing model: {model}")
        print(f"Existing in DB: {bool(existing)}")

        folder_name = np.random.randint(1,10)
        BASE_URL = f"http://127.0.0.1:5000/static/{folder_name}"
        default_images = [
            f"{BASE_URL}/main.jpeg",
            f"{BASE_URL}/side_view.jpeg",
            f"{BASE_URL}/top_view.jpeg",
            f"{BASE_URL}/close_up.jpeg",
            f"{BASE_URL}/table_view.jpeg"
        ]

        if not existing:
            extra = fetched_map.get(model)
            print(f"Storing new laptop model: {bool(extra)}")
            if extra:
                doc.update(extra)
                print(f"✅ Added detailed specs for: {model}")
            else:
                print(f"⚠️ No extra details found for {model}")

            doc["images"] = default_images
            added += 1
        else:
            # if(extra):
            #     doc.update(extra)
            #     print(f"✅ Merged detailed specs for existing model: {model}")
            updated += 1
            doc["images"] = existing.get("images", default_images)

        doc["request_id"] = request_id

        laptops_collection.update_one(
            {"model": model},
            {"$set": doc},
            upsert=True
        )

    print(f"\nLaptop recommendations stored/updated successfully.")
    print(f"📦 Added: {added}, 🔁 Updated: {updated}\n")

    # Step 5: Link User to Recommendations (in users_collection)
    try:
        from bson import ObjectId

        form_input = parse_query_str(query_str)
        
        if user_id:
            user_oid = ObjectId(user_id) 
            recommended_list = [
                {"model": model, "form_input": form_input}
                for model in item_map.keys()
            ]

            users_collection.update_one(
                {"_id": user_oid},
                # Pushing all 5 items to preserve the order and context of this specific request
                {"$push": {"recommended": {"$each": recommended_list}}},
                upsert=True
            )
            print(f"✅ Stored {len(recommended_list)} recommendations for user {user_id} with context.")
        else:
            print("Skipping user recommendation linkage (user not logged in).")

    except Exception as e:
        print(f"⚠️ Failed to update user recommendations history: {e}")

# 🛑 NEW FUNCTION: Performs the required merge for the /laptops route
def get_merged_recommendations_for_user(user_id):
    """
    Fetches the 5 most recent recommendations for a user, merges the product
    specs from laptops_collection with the query context from users_collection.
    """
    from bson import ObjectId
    try:
        user_oid = ObjectId(user_id)
        
        # 1. Fetch user document, only retrieving the last 5 recommended entries
        user_doc = users_collection.find_one(
            {"_id": user_oid}, 
            {"recommended": {"$slice": -5}, "_id": 0} 
        )
        
        if not user_doc or not user_doc.get("recommended"):
            return []

        recent_history = user_doc["recommended"]
        
        # 2. Map models to their specific form_input context
        model_to_context_map = {
            item['model']: item.get('form_input', {}) 
            for item in recent_history if 'model' in item
        }
        model_list = list(model_to_context_map.keys())

        if not model_list:
            return []
            
        # 3. Fetch full laptop documents for these models
        laptop_cursor = laptops_collection.find({"model": {"$in": model_list}})
        laptops_data = list(laptop_cursor)
        
        merged_laptops = []
        
        # 4. Merge product details with the user's form_input context
        for laptop in laptops_data:
            model = laptop.get("model")
            context = model_to_context_map.get(model)
            
            if context is not None:
                # 🛑 Attach the form_input from the user's history
                laptop["form_input"] = context
                
                # Convert ObjectId to string for JSON serialization
                if "_id" in laptop:
                    laptop["_id"] = str(laptop["_id"])
                    
                merged_laptops.append(laptop)
                
        return merged_laptops

    except Exception as e:
        print(f"Error fetching merged recommendations for user {user_id}: {e}")
        return []

# 🛑 REMOVED: get_latest_laptop_recommendations is no longer needed

def parse_query_str(query_str):
    """
    Converts a query string like 'key1: val1 ; key2: val2' into a dictionary.
    """
    # ... (content remains the same) ...
    parsed_dict = {}
    if not query_str:
        return parsed_dict
        
    pairs = query_str.split(' ; ')
    
    for pair in pairs:
        if ': ' in pair:
            key, value = pair.split(': ', 1)
            parsed_dict[key.strip()] = value.strip()
        else:
            parsed_dict['custom_query'] = pair.strip()
            
    return parsed_dict

def update_user_wishlist (user_id, model, action, query_str):
# ... (Content remains the same) ...
    try:
        user_oid = ObjectId(user_id)

        if(action == 'add') :
            form_input = parse_query_str(query_str) 
            
            users_collection.update_one(
                {"_id": user_oid, "wishlist.model": {"$ne": model}},
                {"$push": {"wishlist": {"model": model, "form_input": form_input}}},
                upsert=True
            )
            return True, "Item added to wishlist." 
            
        elif action == "remove" :
            update_res = users_collection.update_one(
                {"_id": user_oid},
                {"$pull": {"wishlist": {"model": model}}}, 
            )
            return update_res.modified_count > 0, "Wishlist updated."
            
        else :
            return False, "Invalid Action."
    
    except Exception as e:
        print(f"Error updating wishlist: {e}")
        return False, str(e)
    
from bson import ObjectId
# Assuming 'users_collection' and 'laptops_collection' are available globally

def get_wishlisted_laptops(user_id):
    """
    Fetches a user's wishlisted laptops, merging the product specs from
    laptops_collection with the form_input context from users_collection.
    """
    try:
        user_oid = ObjectId(user_id)
        
        # 1. Fetch user document, only retrieving the 'wishlist' field
        user_doc = users_collection.find_one(
            {"_id": user_oid},
            {"wishlist": 1},
        )

        if not user_doc or not user_doc.get("wishlist"):
            return []

        wishlist_items = user_doc["wishlist"]
        
        # 2. Map models to their specific form_input context
        # This creates a map: {'model_name': {'cpu_brand': 'Intel', ...}}
        model_to_context_map = {
            item['model']: item.get('form_input', {}) 
            for item in wishlist_items 
            if isinstance(item, dict) and 'model' in item
        }
        
        model_list = list(model_to_context_map.keys())

        if not model_list:
            return []
            
        # 3. Fetch full laptop documents for these models
        # Use $in for efficient look-up of all models
        laptop_cursor = laptops_collection.find({"model": {"$in": model_list}})
        laptops_data = list(laptop_cursor)
        
        merged_laptops = []
        
        # 4. Merge product details with the user's form_input context
        for laptop in laptops_data:
            model = laptop.get("model")
            context = model_to_context_map.get(model)
            
            if context is not None:
                # Attach the form_input from the user's history
                laptop["form_input"] = context
                
                # Convert ObjectId to string for JSON serialization
                if "_id" in laptop:
                    laptop["_id"] = str(laptop["_id"])
                    
                merged_laptops.append(laptop)
                
        return merged_laptops

    except Exception as e:
        # Log the error for debugging (e.g., failed ObjectId conversion)
        print(f"An error occurred: {e}") 
        return []


print("MongoDB connection initialized.")