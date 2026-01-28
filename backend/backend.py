from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import os
from Laptop_Bot import run_query, answers_to_query, QUESTIONNAIRE, ask_questionnaire, fetch_laptop_details
from functools import wraps 
from flask import send_file, abort
from reviews.analysis import process_models
import threading
PROCESSING_TASKS = set()
import threading # Ensure threading is imported if the plan is to use it

# ----------------------------------------------------------------------
# NEW: JWT Configuration
# ----------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "your_fallback_super_secret_key")
if SECRET_KEY == "your_fallback_super_secret_key":
    print("WARNING: Using fallback SECRET_KEY. Set a secure one in keys.env!")

# We need to import the new function from db_mongo here
from db_mongo import (
    store_initial_request, 
    store_bot_response, 
    # REMOVED: get_latest_laptop_recommendations is gone
    get_merged_recommendations_for_user, # <-- NEW IMPORT for authenticated retrieval
    create_user, 
    get_user_by_username, 
    verify_password,
    update_user_wishlist,
    get_wishlisted_laptops,
    store_laptop_recommendations # Also ensure this is available for the non-threaded /query
)

# --- Configuration ---
app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- Utility Functions and Decorators ---

# @app.after_request
# def add_no_cache_headers(response: Response) -> Response:
#     """
#     Adds headers to the response to explicitly tell the client (browser)
#     to never cache the content, forcing a fresh download every time.
#     This prevents 304 Not Modified responses.
#     """
    
#     # Standard header to prevent caching in modern browsers
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
#     # Header for compatibility with HTTP/1.0
#     response.headers["Pragma"] = "no-cache"
    
#     # Header to set an expired date (also for older systems)
#     response.headers["Expires"] = "0"
    
#     # Optional: If you want to set an explicit expiration date in the past
#     # now = datetime.datetime.now()
#     # response.headers["Expires"] = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
#     return response

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "Authorization token is missing or invalid"}), 401

        token = auth_header.split(' ')[1]

        try:
            # 2. Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Pass the user_id (or entire payload) to the wrapped function
            request.user_id = data.get('user_id')
            
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated 

# --- Wishlist Endpoints (No changes needed here as they were already correct) ---

@app.route("/wishlist/<model>", methods=["POST", "DELETE"])
@auth_required
def toggle_wishlist(model):
    user_id = request.user_id
    data = request.json or {}

    if not model:
        return jsonify({"message": "Missing laptop model identifier"}), 400
        
    action = 'add' if request.method == 'POST' else 'remove'
    query_str = data.get('query_str')

    if action == 'add' and not query_str:
        return jsonify({"message": "Missing query_str in payload for adding to wishlist"}), 400

    success, message = update_user_wishlist(user_id, model, action, query_str=query_str)
    
    if success:
        return jsonify({"message": f"Laptop {model} {action}ed to wishlist."}), 200
    else:
        return jsonify({"message": f"Failed to update wishlist: {message}"}), 400
    
@app.route("/wishlist/<model>", methods=["OPTIONS"])
def wishlist_options_handler_model(model):
    return '', 200
    
@app.route("/wishlist", methods=["GET"])
@auth_required
def get_user_wishlist():
    user_id = request.user_id 
    
    wishlist_laptops = get_wishlisted_laptops(user_id)
    
    return jsonify(wishlist_laptops), 200

# --- Search Endpoint ---

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_ip = request.remote_addr
    
    if "answers" in data:
        query_str = answers_to_query(data["answers"])
        keyword = query_str
    elif "custom_query" in data:
        query_str = data["custom_query"]
        keyword = query_str
    else:
        return jsonify({"error": "No query provided"}), 400

    request_id = store_initial_request(user_ip, keyword)
    resp_json = run_query(query_str, return_json=True)
    store_bot_response(request_id, str(resp_json))

    # Store each laptop as a separate document
    if "items" in resp_json:
        # 1. Extract user_id from the Authorization header if present
        user_id = None 
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
             try:
                 token = auth_header.split(" ")[1]
                 token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                 user_id = token_data.get("user_id")
             except Exception as e:
                 print(f"Error decoding JWT in /query: {e}")
                 pass

        # 2. Pass the extracted user_id to the store function
        store_laptop_recommendations(
            request_id, 
            resp_json["items"], 
            query_str, 
            user_id=user_id  # <--- CRITICAL FIX: Passing user_id here
        ) 
        model_names = [item.get("model") for item in resp_json["items"] if "model" in item]

        print("🖥️ Model names:", model_names)
        
        # process_models(model_names)
        threading.Thread(target=process_models, args=(model_names,), daemon=True).start()

        
    return jsonify(resp_json)

# --- Laptop Retrieval Endpoint ---

@app.route("/laptops", methods=["GET"])
def get_laptops():
    # 1. Check for Authorization header and attempt to decode user_id
    auth_header = request.headers.get('Authorization')
    user_id = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = token_data.get('user_id')
        except Exception:
            # Token is expired/invalid, treat as anonymous
            pass

    if user_id:
        # 2. Authenticated user: use the personalized, merged function
        laptops = get_merged_recommendations_for_user(user_id)
    else:
        # 3. Anonymous user: return an empty list (as the old global function is gone)
        laptops = []
    
    if not laptops:
        return jsonify({"message": "No recent recommendations available. Please log in or run a search."}), 200

    # The get_merged_recommendations_for_user already converts ObjectId to string, 
    # so no need for the loop here.
    return jsonify(laptops), 200

# --- Auth Endpoints ---

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    success, message = create_user(username, password)
    
    if success:
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": message}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = get_user_by_username(username)

    if user and verify_password(password, user["password"]):
        token_payload = {
            "user_id": str(user["_id"]),
            "username": user["username"],
            "exp": datetime.utcnow() + timedelta(hours=24) 
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "token": token, 
            "message": "Login successful"
        }), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401 
    
@app.route('/api/reviews/analysis/<modelname>', methods=['GET'])
def get_review_analysis(modelname):
    # 1. Setup Paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "reviews", "json_files", "unified_analysis"))
    safe_modelname = modelname.replace(" ", "_")
    filename = f"{safe_modelname}_unified.json"
    file_path = os.path.join(base_dir, filename)

    # 2. Security Check
    if not os.path.commonpath([base_dir, os.path.abspath(file_path)]) == base_dir:
        return abort(403, description="Access forbidden: Invalid file path.")

    # 3. Check if file exists
    if os.path.isfile(file_path):
        print(f"✅ Serving analysis for: {modelname}")
        return send_file(file_path, mimetype='application/json')

    # 4. FILE NOT FOUND - TRIGGER ON-DEMAND PROCESSING
    print(f"⚠️ Analysis not found for: {modelname}")

    if modelname in PROCESSING_TASKS:
        print(f"⏳ Analysis is already running for {modelname}. Client should retry...")
    else:
        print(f"🚀 Triggering background analysis for {modelname}...")
        
        # Add to tracking set
        PROCESSING_TASKS.add(modelname)

        # Define a wrapper to run analysis and clean up the set afterwards
        def run_and_cleanup(name):
            try:
                # Run the actual heavy lifting
                process_models([name]) 
            except Exception as e:
                print(f"❌ Error during on-demand analysis for {name}: {e}")
            finally:
                # Remove from tracking set so it can be retried if needed later
                if name in PROCESSING_TASKS:
                    PROCESSING_TASKS.remove(name)

        # Start the thread
        threading.Thread(target=run_and_cleanup, args=(modelname,), daemon=True).start()

    # Return 404 so your React Frontend "catch" block triggers the retry/polling logic
    return abort(404, description="Analysis processing started. Please retry shortly.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)