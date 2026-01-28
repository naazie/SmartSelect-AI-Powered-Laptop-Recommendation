import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai
# from tabulate import tabulate
from questionnaire import QUESTIONNAIRE, ask_questionnaire

dotenv_path = os.path.join(os.path.dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

# --- First Gemini Bot ---
API_KEY = os.getenv("API_KEY_FIRST")
if not API_KEY:
    raise ValueError("API_KEY_FIRST not found in keys.env")

genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel("gemini-2.5-pro")
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# --- Second Gemini Bot ---
API_KEY_SECOND = os.getenv("API_KEY_SECOND")
if not API_KEY_SECOND:
    raise ValueError("API_KEY_SECOND not found in keys.env")

# No separate client; we'll reconfigure before using it.
# details_model_name = "gemini-2.5-flash-lite"
# details_model_name = "gemini-2.5-flash"
details_model_name = "gemini-flash-latest"


# ------------------ PROMPTS ------------------
PROMPT = """You are a Laptop Recommendation Expert.
You will be provided with user requirements and your job is to recommend the best laptop models based on the user's needs.
Return ONLY valid JSON (no prose, no markdown fences).
Schema:
{
  "query": string,
  "items": [
    {
        "model": string,
        "price_inr": string,
        "why": string
    }
  ]
}

Compulsory Rules:
- Keep the search limited to lenovo laptops only and as for model, include lenovo in the model name with the series name.
- If budget is mentioned, filter accordingly assuming that India is the location.
- "model": give the exact laptop model name.
- List top 5 relevant laptops.
- If unsure about a spec or price, give us the predicted value for the model.
- Model name strictly should be the first to be mentioned.
- In **price_inr**, give approximate price in INR, strictly.
- In "why", explain clearly and simply 'why this laptop fits the user's need', be descriptive, use non-technical terms, and highlight features that matter for them.
- In "why", the range of the words should be between 20 to 25 words.
"""

DETAILS_PROMPT = """You are a Laptop Specification Expert.
You will receive a list of laptop model names.
For each model, return detailed specs in JSON format with this schema:
{
  "model": string,
  "cpu": string,
  "ram": string,
  "storage": string,
  "gpu": string,
  "display": string,
  "battery": string,
  "Why_in": string,
  "what_it_says": {
        "CPU_in": string,
        "RAM_in": string,
        "Storage_in": string,
        "GPU_in": string,
        "Display_in": string,
        "Battery_in": string,
        "Overall_in": string
  }
}

Rules & Guidelines:

1. **"Model"** -> Include the complete laptop model or series name (do include lenovo in the name)(e.g., "IdeaPad Slim 5", "ThinkBook 14 Gen 2").

2. **"CPU"**, **"RAM"**, **"Storage"**, **"GPU"**, **"Display"**, and **"Battery"** -> Clearly describe each of the key technical specifications for the laptop. Avoid generic answers - specify the actual configuration wherever possible (e.g., "Intel Core i5 13th Gen" instead of just "Intel processor").

3. **"What it Says"** -> Provide a breakdown of what each key specification means in simple, non-technical language for easy understanding:
   - Explain the *technical meaning* of each feature (CPU, GPU, RAM, etc.) and what it implies in real-world performance.
   - For every feature, analyze the listed details and explain:
     # What the **average** specification for that feature typically is in similar laptops.  
     # How this laptop's configuration compares to that average.  
     # Whether it is **good**, **average**, or **best suited** for the user's purpose and budget.  
   - If a better option exists that may exceed the user's price range, mention it clearly, for example:  
     "Upgrading to 16GB RAM would improve multitasking but may push the price above your range (₹65,000 - ₹70,000)."
   - Keep each feature's explanation clear and practical - focus on what it means for everyday use (speed, multitasking, gaming, portability, etc.).
   - Conclude the section with an **overall performance rating** in plain words such as "excellent", "good", "average", or "below average".  
     Example: "Overall performance: good."

4. **"Why"** -> Write a detailed, easy-to-understand explanation (minimum 200 words) describing:
   - Why this laptop is suitable or unsuitable for specific types of users (students, programmers, professionals, gamers, etc.).
   - Highlight both **strengths** (e.g., great battery life, strong CPU performance, portability) and **weaknesses** (e.g., limited storage, not ideal for gaming, shorter battery life).
   - Use clear, simple, conversational language - avoid heavy technical jargon.
   - Example:  
     "This laptop is a good option for students and professionals who want smooth multitasking and strong battery life. It's not ideal for gaming or graphics-heavy work since it relies on integrated graphics. Its compact design and fast SSD make it reliable for daily tasks."

**Compulsory Rules:**
- Every field must be filled. If an exact detail is unavailable, use a **best-predicted value** or **realistic approximation**.
- Do **not** leave any field blank under any circumstance.
- Output **only valid JSON** - no additional explanations, commentary, or markdown formatting.
"""

# ------------------ UTILS ------------------
def build_prompt(user_query: str) -> str:
    return PROMPT + f'\nUser Query: "{user_query}"\nJSON:'

def extract_json(txt: str):
    m = re.search(r'(\{.*\}|\[.*\])', txt, re.DOTALL)
    return m.group(1) if m else txt

def answers_to_query(answers: dict) -> str:
    query_parts = []
    for k, v in answers.items():
        if isinstance(v, list):
            query_parts.append(f"{k}: {', '.join(v)}")
        else:
            query_parts.append(f"{k}: {v}")
    return " ; ".join(query_parts)

# ------------------ MAIN BOT ------------------
def run_query(q: str, return_json=False):
    resp = model.generate_content(build_prompt(q))
    raw = resp.text or ""
    js = extract_json(raw).strip()

    try:
        data = json.loads(js)
    except Exception:
        return {"error": "Failed to parse model output", "raw": raw}
    
    print("\nLaptop Recommendations:")
    print(json.dumps(data, indent=2))

    if return_json:
        return data
    
    print("\nLaptop Recommendations:")
    print(json.dumps(data, indent=2))

    items = data.get("items", [])
    if items:
        fetch_laptop_details(items, q)

def fetch_laptop_details(items, q: str="", return_json=False):
    models = [it.get("model") for it in items if it.get("model")]
    if not models:
        print("No laptop models found to fetch details for.")
        return
    
    # print("\nFetching detailed specifications for each model...\n")
    # query = DETAILS_PROMPT + "\nModels:\n" + "\n".join(models) + "\nJSON:"
    query = (
        f"{DETAILS_PROMPT}\n"
        f"User Query:\n{q}\n\n"
        f"Models:\n" + "\n".join(models) + "\n\nJSON:"
    )
    
    genai.configure(api_key=API_KEY_SECOND)
    details_model = genai.GenerativeModel(details_model_name)

    resp = details_model.generate_content(query)
    raw = resp.text or ""
    js = extract_json(raw).strip()
    try:
        details_data = json.loads(js)
    except Exception:
        print("Error parsing details response.\nRaw output:\n", raw)
        return
    
    # print("\nDetailed Laptop Specifications:")
    # print(json.dumps(details_data, indent=2))

    if return_json:
        return details_data
    
    print("\nDetailed Laptop Specifications:")
    print(json.dumps(details_data, indent=2))

# ------------------ ENTRY ------------------
if __name__ == "__main__":
    print("Laptop Bot using Questionnaire\n")

    user_answers = ask_questionnaire(QUESTIONNAIRE["questions"])
    query_str = answers_to_query(user_answers)
    
    print("\nThanks! Searching for the best laptops based on your preferences...\n")
    run_query(query_str)
    
    print("\nYou can now modify the query or add more preferences (type 'q' to quit).")
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            break
        
        if not user_input or user_input.lower() in {"q", "quit", "exit"}:
            break
        
        updated_query = query_str + " ; " + user_input
        print("\nSearching with updated preferences...\n")
        run_query(updated_query)