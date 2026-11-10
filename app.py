import os
import sqlite3
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "conversations.db"
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "12"))

SYSTEM_PROMPT = """
You are DevMate, a practical coding mentor for students and early-career developers.
Explain concepts accurately, use clear step-by-step reasoning, and prefer working,
maintainable examples. Ask a focused question when requirements are unclear.
Point out incorrect assumptions instead of agreeing blindly. Never claim code was
tested unless it actually was. Keep answers focused and distinguish facts from guesses.
""".strip()

app = FastAPI(title="DevMate LLM Chatbot", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    context_messages_sent: int


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'model')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id)
        """)


initialize_database()


def get_recent_history(conversation_id: str):
    with get_db() as db:
        rows = db.execute(
            """
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (conversation_id, MAX_HISTORY_MESSAGES),
        ).fetchall()
    return list(reversed(rows))


def save_message(conversation_id: str, role: str, content: str):
    with get_db() as db:
        db.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Add GEMINI_API_KEY to your .env file.",
        )

    conversation_id = request.conversation_id or str(uuid.uuid4())
    history = get_recent_history(conversation_id)

    # Include the new user turn in the model request, but only persist it
    # after a successful API response so failed calls do not corrupt history.
    contents = [
        types.Content(
            role=row["role"],
            parts=[types.Part.from_text(text=row["content"])],
        )
        for row in history
    ]
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=request.message)],
        )
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        reply = (response.text or "").strip()
        if not reply:
            raise RuntimeError("The model returned an empty response.")
    except Exception as exc:
        # Log the technical detail on the server, but do not expose secrets
        # or raw provider errors to the browser.
        print(f"Gemini request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The AI service could not complete your request. Check your connection or API quota, then try again.",
        ) from exc

    save_message(conversation_id, "user", request.message)
    save_message(conversation_id, "model", reply)

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        context_messages_sent=len(contents),
    )


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    with get_db() as db:
        rows = db.execute(
            """
            SELECT role, content, created_at FROM messages
            WHERE conversation_id = ? ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()
    return {"conversation_id": conversation_id, "messages": [dict(row) for row in rows]}
