# DevMate: LLM API Integration

A multi-turn chatbot built with **FastAPI**, **Google Gemini**, and **SQLite**.

## Features

- Real Gemini API integration through the official `google-genai` SDK.
- Separate conversation IDs so messages from different chats do not mix.
- SQLite persistence: conversation history survives server restarts.
- Context-window management: only the most recent 12 messages are sent to Gemini by default.
- A system instruction defines the bot as a practical coding mentor.
- Clear API and browser-side error messages.
- API key loaded from `.env`; `.env` is excluded from Git.

## Requirements

- Python 3.10+
- A Gemini API key from Google AI Studio: https://aistudio.google.com/app/apikey

## Run locally

### 1. Create and activate a virtual environment

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure your API key

Copy `.env.example` to `.env`:

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS / Linux**
```bash
cp .env.example .env
nano .env
```

Replace the placeholder with your **newly generated** Gemini API key. Do not commit `.env`.

### 4. Start the application

```bash
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"My name is Alex. Remember that for this chat."}'
```

Use the returned `conversation_id` in the next request:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"PASTE_ID_HERE","message":"What is my name?"}'
```

## Context-window strategy

The backend retrieves at most `MAX_HISTORY_MESSAGES` previous messages (12 by default) for the selected conversation, then appends the current user message. Change the limit in `.env` if needed. This keeps the request bounded instead of sending unlimited history.

## Verify the required 5-turn conversation

Try these messages in the browser, one at a time:

1. `My name is Alex and I am building a Python expense tracker.`
2. `The app uses FastAPI for its backend.`
3. `I want to store transactions in SQLite.`
4. `What database did I choose?`
5. `Summarise what you know about my project and my name.`

The bot should recall details from earlier turns. For stronger verification, restart the server and continue the same conversation; the conversation ID is kept in the browser session and messages are stored in SQLite.

## Error handling

- Missing or placeholder API key returns HTTP 503 with setup guidance.
- Requests have a configurable timeout (`GEMINI_TIMEOUT_SECONDS`, default 30s) returning HTTP 504 on timeout.
- Provider/network/quota failures return HTTP 502 with a user-readable message.
- Failed API calls are not written to the conversation history.
- Technical provider errors are logged by the backend, not exposed directly to the browser.

## Before submitting

- [ ] Add your own `.env` locally and verify the chatbot works.
- [ ] Confirm `.env` is ignored: `git check-ignore .env`
- [ ] Complete at least five turns and verify earlier context is recalled.
- [ ] Confirm no API key appears in tracked files or Git history.
- [ ] Push the project to a **public** GitHub repository.
- [ ] Submit the repository URL and the honest AI usage declaration.

## Tech stack

Python, FastAPI, Google Gemini API, SQLite, HTML/CSS/JavaScript.
