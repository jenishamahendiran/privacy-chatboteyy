import os
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

# Simple PII masking layer.
# This is intentionally transparent and easy to extend.
PATTERNS = [
    (r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[EMAIL]'),
    (r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', '[PHONE]'),
    (r'\b\d{12}\b', '[ID_NUMBER]'),
]

def mask_pii(text):
    masked = text
    for pattern, replacement in PATTERNS:
        masked = re.sub(pattern, replacement, masked, flags=re.I)
    return masked

def generate_demo_response(message):
    """Safe demo response so the project runs without an API key."""
    return (
        "This is the privacy-first demo mode. I received your question after "
        "the privacy layer processed it.\n\n"
        f"Processed message: {message}\n\n"
        "To connect a real LLM, add your model/API integration in this function."
    )

def generate_ai_response(message):
    # Gemini integration is optional. The app falls back to demo mode.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_demo_response(message)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            contents=(
                "You are a privacy-first helpful AI assistant. "
                "Do not request unnecessary personal information. "
                "Answer the user's question clearly.\n\n"
                f"User message: {message}"
            ),
        )
        return response.text
    except Exception as exc:
        return f"AI service error: {exc}\n\nDemo response:\n{generate_demo_response(message)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    original = str(data.get("message", "")).strip()

    if not original:
        return jsonify({"error": "Message cannot be empty."}), 400

    masked = mask_pii(original)
    answer = generate_ai_response(masked)

    return jsonify({
        "answer": answer,
        "privacy": {
            "pii_masking_applied": masked != original,
            "processed_message": masked
        }
    })

@app.post("/api/clear")
def clear():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
