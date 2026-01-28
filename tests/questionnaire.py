# questionnaire.py
QUESTIONNAIRE = {
  "questions": [
    {
      "id": "use_case",
      "question": "What do you mainly need the laptop for?",
      "type": "single-choice",
      "options": [
        "For everyday tasks (browsing, movies, office work)",
        "For studies or programming",
        "For gaming or watching high-quality videos",
        "For design, video editing, or creative work",
        "Other"
      ]
    },
    {
      "id": "budget",
      "question": "What is your budget range?",
      "type": "single-choice",
      "options": [
        "₹35,000 – ₹50,000 (Basic use)",
        "₹55,000 – ₹75,000 (Good performance)",
        "₹80,000 – ₹1,20,000 (High-end use)",
        "Above ₹1,30,000 (Premium laptops)",
        "Not sure yet"
      ]
    },
    {
      "id": "processor",
      "question": "What type of processor do you prefer?",
      "type": "single-choice",
      "options": [
        "Basic – for light use (Intel i3 / Ryzen 3)",
        "Medium – for smooth multitasking (Intel i5 / Ryzen 5)",
        "Powerful – for heavy work or gaming (Intel i7 / Ryzen 7 or above)"
      ]
    },
    {
      "id": "ram",
      "question": "How much memory (RAM) do you prefer?",
      "type": "single-choice",
      "options": [
        "8GB (Good for normal use)",
        "16GB (Best for multitasking and coding)",
        "32GB or more (For professional or creative work)"
      ]
    },
    {
      "id": "gpu",
      "question": "Do you need a graphics card?",
      "type": "single-choice",
      "options": [
        "No, normal use is fine",
        "Yes, for gaming, video editing, or graphics-heavy work"
      ]
    },
    {
      "id": "screen_size",
      "question": "What screen size do you prefer?",
      "type": "single-choice",
      "options": [
        "Compact (13–14 inches, easy to carry)",
        "Standard (15–16 inches, balanced size)",
        "Large (17 inches or more, for bigger display)"
      ]
    },
    {
      "id": "battery",
      "question": "How important is battery life to you?",
      "type": "single-choice",
      "options": [
        "Needs to last long (8–10 hours)",
        "Average battery is fine (5–7 hours)",
        "Mostly use plugged in (not important)"
      ]
    },
    {
      "id": "weight",
      "question": "Do you prefer a lightweight or heavy laptop?",
      "type": "single-choice",
      "options": [
        "Lightweight (easy to carry, below 1.6 kg)",
        "Medium (1.6–2.5 kg, balanced)",
        "Doesn’t matter to me"
      ]
    },
    {
      "id": "priorities",
      "question": "What matters most to you while choosing a laptop?",
      "type": "multi-choice",
      "options": [
        "Fast performance",
        "Long battery life",
        "Lightweight and portable",
        "Good display quality",
        "Affordable price"
      ]
    },
    {
      "id": "other_requirements",
      "question": "Any other preferences? (Example: touchscreen, color, 2-in-1, stylus support, etc.)",
      "type": "text"
    }
  ]
}

def ask_questionnaire(questions):
    answers = {}
    for q in questions:
        print("\n" + q["question"])
        if q["type"] in ["single-choice", "multi-choice"]:
            for i, option in enumerate(q["options"], 1):
                print(f"{i}. {option}")
        if q["type"] == "single-choice":
            while True:
                try:
                    choice = int(input("Enter choice number: ").strip())
                    if 1 <= choice <= len(q["options"]):
                        answers[q["id"]] = q["options"][choice - 1]
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Enter a number.")
        elif q["type"] == "multi-choice":
            print("Enter numbers separated by comma (e.g., 1,3):")
            while True:
                inp = input("Your choice(s): ").strip()
                try:
                    indices = [int(x) for x in inp.split(",") if x.strip().isdigit()]
                    valid_indices = [i for i in indices if 1 <= i <= len(q["options"])]
                    if valid_indices:
                        answers[q["id"]] = [q["options"][i - 1] for i in valid_indices]
                        break
                    else:
                        print("Invalid choice(s). Try again.")
                except ValueError:
                    print("Enter numbers separated by commas.")
        elif q["type"] == "text":
            ans = input("Your answer: ").strip()
            answers[q["id"]] = ans
    return answers
