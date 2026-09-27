# PrivacyFirst AI Chatbot

A beginner-friendly Flask chatbot designed around a privacy-first architecture.

## Features

- ChatGPT-style web interface
- Flask backend
- PII masking for common email/phone/ID patterns
- Gemini API integration is optional
- Demo mode works without an API key
- Memory is not persisted by the starter project
- Clear separation between privacy layer and AI layer

## 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Gemini (optional)

Copy `.env.example` to `.env`.

Then add your Gemini API key:

```text
GEMINI_API_KEY=your-api-key-here
```

If you don't add a key, the chatbot runs in demo mode.

## 4. Run

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## Architecture

User
  -> Web UI
  -> Flask API
  -> Privacy / PII Masking
  -> Gemini or another LLM
  -> Response
  -> Web UI

## Important project note

This starter uses regex-based masking only. For a serious production system,
replace or supplement it with a robust PII detection system, add authentication,
secure secret management, HTTPS, rate limiting, audit controls, data-retention
policies, and proper security testing.

The goal is to make data handling explicit and user-controlled—not to claim that
any external AI API is automatically private.
