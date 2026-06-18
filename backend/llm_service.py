import ollama
import asyncio
from typing import List, Dict, Any

# Import the shared Motor DB instance (matches import style used in main.py)
from database import db


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


def generate_llama_response(user_input, context_docs):
    """
    Feeds the user input and the context layer (chat history) into Llama 3.2 3B.
    Enforces mental health app UX standards: short paragraphs, clean spacing,
    and a strict maximum of one question at the very end.
    """
    system_prompt = (
        "You are an empathetic, supportive, and grounded mental well-being companion chatbot. "
        "Help the user navigate their thoughts and emotions safely and gently.\n\n"
        + SYSTEM_PROMPT_RULES + "\n"
    )

    if context_docs:
        system_prompt += f"CHAT HISTORY / CONTEXT:\n{context_docs}\n\n"

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input},
            ],
            options={
                'temperature': 0.6,
                'num_ctx': 4096
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"LLM Error: {str(e)}"


def generate_greeting(user_name, memory):
    # Return a static, short welcome message using the provided user name
    return f"Hey {user_name}, welcome back! How are things tracking today?"


    # ---------------------------------------------------------------------------
    # Dynamic database retrieval + dynamic prompt generation
    # ---------------------------------------------------------------------------
    async def fetch_latest_conversation_thread(user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the single most recent conversation thread for `user_id`.

        Logic:
        1. Find the single most recent session document for the user sorted by
           `timestamp` descending (the absolute latest record).
        2. Take its `session_id` and fetch all documents that share that
           `session_id` for the same user, returning them ordered by timestamp
           ascending (the chronological thread).

        This function is completely dynamic and does NOT hardcode topic names
        or rely on any prior example rule ordering.
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
        Formats a list of session documents into a clean, compact context string
        for the model. Keeps order chronological and avoids injecting any
        hardcoded topic labels. Each turn is prefixed with speaker and timestamp.
        """
        lines = []
        for d in thread_docs:
            ts = d.get("timestamp")
            # Normalize timestamp to ISO if possible
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

        This template is topic-agnostic: it asks the model to identify the
        user's most recent message and reflect that specific theme/emotion
        dynamically. It includes the shared `SYSTEM_PROMPT_RULES` for UX.
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
        Synchronous wrapper that fetches the latest thread and asks Ollama to
        summarize the user's most recent emotion/theme dynamically.
        """
        try:
            thread_docs = asyncio.run(fetch_latest_conversation_thread(user_id))
        except Exception:
            thread_docs = []

        if not thread_docs:
            return "I don't have any recent messages to summarise right now. How are you feeling today?"

        context_text = format_thread_for_model(thread_docs)
        system_prompt = build_dynamic_emotion_system_prompt(context_text)

        try:
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': 'Please produce the Theme / Summary / Question as instructed.'}
                ],
                options={'temperature': 0.5, 'num_ctx': 4096}
            )
            return response['message']['content']
        except Exception as e:
            return f"LLM Error: {str(e)}"