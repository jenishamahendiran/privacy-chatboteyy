import os
import re

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
PATTERNS = [

# Secret key for Flask sessions
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)


# ============================================================
# PRIVACY / PII PROTECTION
# ============================================================

PII_PATTERNS = [
    # Email addresses
    (
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
        '[EMAIL]'
    ),

    # Indian phone numbers
    (
        r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b',
        '[PHONE]'
    ),

    # 12-digit ID numbers
    (
        r'\b\d{12}\b',
        '[ID_NUMBER]'
    ),

    # Simple credit/debit card-like number
    (
        r'\b(?:\d[ -]*?){13,19}\b',
        '[CARD_NUMBER]'
    )
]


def mask_pii(text):
    """
    Detect and mask common personally identifiable information.
    """

    masked_text = text

    for pattern, replacement in PII_PATTERNS:
        masked_text = re.sub(
            pattern,
            replacement,
            masked_text,
            flags=re.IGNORECASE
        )

    return masked_text


# ============================================================
# DEMO RESPONSE
# ============================================================

def generate_demo_response(message):
    """
    Used when Gemini API key is not configured.
    """

    return (
        "🔐 PrivacyFirst AI is running in DEMO mode.\n\n"
        "Your message was processed through the privacy layer.\n\n"
        f"Processed message:\n{message}\n\n"
        "To enable real AI responses, add your Gemini API key "
        "to the Render environment variables."
    )


# ============================================================
# GEMINI AI RESPONSE
# ============================================================

def generate_ai_response(message):

    api_key = os.getenv("GEMINI_API_KEY")

    # If API key is missing, use demo mode
    if not api_key:
        return generate_demo_response(message)

    try:

        from google import genai

        client = genai.Client(
            api_key=api_key
        )

        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.1-flash-lite"
        )

        system_instruction = """
You are PrivacyFirst AI, a privacy-focused conversational assistant.

Important rules:

1. Do not ask for unnecessary personal information.
2. Do not request passwords, API keys, banking information,
   authentication codes, or other sensitive information.
3. Treat placeholders such as [EMAIL], [PHONE], and
   [ID_NUMBER] as masked private information.
4. Answer the user's question clearly and naturally.
5. Never claim that the system is completely private or
   completely anonymous.
6. Explain privacy limitations honestly when relevant.
"""

        prompt = f"""
{system_instruction}

User message:

{message}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "I couldn't generate a response."

    except Exception as error:

        print("Gemini error:", error)

        return (
            "⚠️ The AI service could not be reached.\n\n"
            "Please check your Gemini API configuration."
        )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# CHAT API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        original_message = str(
            data.get("message", "")
        ).strip()

        # Empty message check
        if not original_message:

            return jsonify({
                "error": "Message cannot be empty."
            }), 400

        # ----------------------------------------------------
        # STEP 1: Privacy processing
        # ----------------------------------------------------

        masked_message = mask_pii(
            original_message
        )

        pii_detected = (
            masked_message != original_message
        )

        # ----------------------------------------------------
        # STEP 2: Send ONLY masked message to AI
        # ----------------------------------------------------

        answer = generate_ai_response(
            masked_message
        )

        # ----------------------------------------------------
        # STEP 3: Return response
        # ----------------------------------------------------

        return jsonify({

            "answer": answer,

            "privacy": {

                "pii_masking_applied": pii_detected,

                "processed_message": masked_message

            }

        })

    except Exception as error:

        print("Chat error:", error)

        return jsonify({
            "error": "An unexpected server error occurred."
        }), 500


# ============================================================
# CLEAR SESSION
# ============================================================

@app.route("/api/clear", methods=["POST"])
def clear_chat():

    session.clear()

    return jsonify({
        "ok": True,
        "message": "Conversation cleared."
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "PrivacyFirst AI"
    })


# ============================================================
# LOCAL + RENDER SERVER
# ============================================================

if __name__ == "__main__":

    # Render provides PORT automatically.
    # Local computer will use 5000.

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )