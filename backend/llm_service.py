import os
import httpx
import asyncio
from typing import List, Dict, Any

# Import the shared Motor DB instance (matches import style used in main.py)
from database import db

# --- Cloud API Configuration for Groq ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant" # Groq's high-speed cloud Llama 3.2 instance

# ---------------------------------------------------------------------------
# Shared system prompt – enforces mental-health UX formatting standards
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_RULES = (
    "CRITICAL RESPONSE FORMATTING RULES:\n"
    "1. SHORT PARAGRAPHS: Every paragraph must be extremely concise, containing a MAXIMUM of 2 to 3 sentences.\n"
    "2. CLEAN SPACING: Separate every paragraph with a blank line. "
    "Your closing question MUST be separated from the preceding text by a double line break "
    "(i.e. a completely blank line before it) so it sits entirely on its own line.\n"
    "3. NO REPETITION: Do not echo the user's words back at them. "
    "Avoid cliché pairings like 'on one hand / on the other hand' or repeating 'mix of emotions'.\n"
    "4. STRICT QUESTION LIMIT: You may ask at most ONE question per response. "
    "It MUST be the very last line. No other questions may appear anywhere else in your reply.\n"
)


def generate_llama_response(user_input: str, context_docs: str) -> str:
    """
    Feeds the user input and the context layer (chat history) into Llama 3.2 3B via Groq Cloud API.
    Enforces mental health app UX standards: short paragraphs, clean spacing,
    and a strict maximum of one question at the very end.
    """
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY is missing from environment variables!")
        return "I'm having trouble connecting to my network right now. Can we try again in a moment?"

    system_prompt = (
        "You are an empathetic, supportive, and grounded mental well-being companion chatbot. "
        "Help the user navigate their thoughts and emotions safely and gently.\n\n"
        + SYSTEM_PROMPT_RULES + "\n"
    )

    if context_docs:
        system_prompt += f"CHAT HISTORY / CONTEXT:\n{context_docs}\n\n"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.6,
        "max_tokens": 500
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GROQ_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Groq Request Error: {response.status_code} - {response.text}")
                return "I'm right here with you, but I had a small hiccup processing that. Can you repeat it?"
    except Exception as e:
        return f"LLM Cloud Routing Error: {str(e)}"


def generate_greeting(user_name: str, memory: Dict[str, Any]) -> str:
    """
    Generates a personalized welcoming message using Groq based on historical mental health analytics.
    """
    if not GROQ_API_KEY:
        return f"Hey {user_name}, welcome back! How are things tracking today?"

    system_prompt = (
        f"You are Mirra, a warm, safe wellness companion AI. Create a welcoming, single-paragraph "
        f"greeting for {user_name} (maximum 2 sentences) based on their memory records. "
        f"Keep it grounded, loving, and supportive. Do not include data variables in your prose.\n\n"
        f"User state data summary:\n{memory}"
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Say hello to me."}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(GROQ_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Greeting Generation Error: {e}")
    
    return f"Hey {user_name}, welcome back! How are things tracking today?"


# ---------------------------------------------------------------------------
# Dynamic database retrieval + dynamic prompt generation
# ---------------------------------------------------------------------------
async def fetch_latest_conversation_thread(user_id: str) -> List[Dict[str, Any]]:
    """
    Fetches the single most recent conversation thread for `user_id`.
    """
    collection = db.sessions

    # Step 1: get the absolute latest document for this user
    latest_cursor = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(1)
    latest_list = await latest_cursor.to_list(length=1)
    if not latest_list:
        return []

    latest_doc = latest_list[0]
    session_id = latest_doc.get("session_id")

    # Step 2: fetch the full thread for that session_id in chronological order
    thread_cursor = collection.find({"user_id": user_id, "session_id": session_id}).sort("timestamp", 1)
    thread_docs = await thread_cursor.to_list(length=1000)
    return thread_docs


def format_thread_for_model(thread_docs: List[Dict[str, Any]]) -> str:
    """
    Formats a list of session documents into a clean, compact context string for the model.
    """
    lines = []
    for d in thread_docs:
        ts = d.get("timestamp")
        try:
            ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
        except Exception:
            ts_str = str(ts)

        user_msg = d.get("message", "")
        ai_msg = d.get("ai_reply", "")
        if user_msg:
            lines.append(f"[{ts_str}] User: {user_msg}")
        if ai_msg:
            lines.append(f"[{ts_str}] AI: {ai_msg}")

    return "\n".join(lines)


def build_dynamic_emotion_system_prompt(thread_context: str) -> str:
    """
    Returns a system prompt template that instructs the model to summarise
    and reflect the emotional tone and main theme of the latest thread.
    """
    prompt = (
        "You are an empathetic, concise mental-health companion.\n\n"
        + SYSTEM_PROMPT_RULES
        + (
            f"\n\nTASK:\n"
            "Given the conversation thread provided in the 'THREAD' block, do the following without\n"
            "inventing facts or referencing any application-specific keywords:\n"
            "1) Identify the user's absolute most recent message (the last User turn) and the primary theme or situation it expresses.\n"
            "2) Provide a one-line theme label (very short).\n"
            "3) Write a concise 2-3 sentence emotional summary that directly reflects that most recent message and its tone.\n"
            "4) End with exactly ONE short check-in question on its own line, separated from the body by a blank line.\n"
            "RESTRICTIONS: Do NOT hardcode or guess topics; use only what appears in the thread. Avoid introducing prior examples or branching logic.\n\n"
            f"THREAD:\n{thread_context}\n\n"
            "OUTPUT FORMAT (strict):\n"
            "Theme: <one-line label>\n\n"
            "Summary: <2-3 short sentences reflecting the user's most recent message>\n\n"
            "Question: <one short question on its own line>\n"
        )
    )
    return prompt


def summarize_latest_thread_sync(user_id: str) -> str:
    """
    Synchronous wrapper that fetches the latest thread and asks Groq to
    summarize the user's most recent emotion/theme dynamically.
    """
    if not GROQ_API_KEY:
        return "I don't have any recent messages to summarise right now. How are you feeling today?"

    try:
        thread_docs = asyncio.run(fetch_latest_conversation_thread(user_id))
    except Exception:
        thread_docs = []

    if not thread_docs:
        return "I don't have any recent messages to summarise right now. How are you feeling today?"

    context_text = format_thread_for_model(thread_docs)
    system_prompt = build_dynamic_emotion_system_prompt(context_text)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Please produce the Theme / Summary / Question as instructed."}
        ],
        "temperature": 0.5,
        "max_tokens": 400
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GROQ_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                return "I'm summarizing our recent chats internally right now. Let's keep exploring how you feel today."
    except Exception as e:
        return f"LLM Error: {str(e)}"