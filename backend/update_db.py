from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "keyword_processor_db")

if not MONGO_URI:
    raise Exception("MONGO_URI not set. Check your .env file and ensure dotenv is installed.")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
laptops_collection = db["laptops"]
users_collection = db["users"]

# Delete all documents from the laptops collection
result = laptops_collection.delete_many({})
print(f"✅ Deleted {result.deleted_count} documents from the laptops collection.")

# Remove 'wishlist' and 'recommended' fields from all users
update_result = users_collection.update_many(
    {},
    {
        "$unset": {"wishlist": "", "recommended": ""}
    }
)
print(f"🧹 Cleared 'wishlist' and 'recommended' fields for {update_result.modified_count} users.")