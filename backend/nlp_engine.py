import spacy
import asyncio
import os
import json
import re
import random
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from collections import Counter
from clinical_analyzer_llama import get_clinical_taxonomy_analysis, format_analysis_for_storage

# Load the model
try:
    nlp = spacy.load("en_core_web_md")
except:
    nlp = spacy.load("en_core_web_sm")

client_ai = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
    http_options=types.HttpOptions(api_version="v1"),
)

# In-memory session context
_MESSAGE_CACHE: Dict[str, Dict[str, Any]] = {}

COZY_GAMES = ["Stardew Valley", "Unpacking", "A Short Hike"]
COZY_SHOWS = ["The Good Place", "Ted Lasso"]

SYSTEM_INSTRUCTION = """
You are a Senior AI Clinical Architect and supportive friend. 
1. If the user asks for a GAME, suggest one of these: Stardew Valley, Unpacking, or A Short Hike.
2. If the user asks for a SHOW, suggest one of these: The Good Place or Ted Lasso.
3. If the user mentions a 'win' (like attendance, marks, or showing up), celebrate it specifically.
4. NEVER repeat the same comfort phrase twice in a row. 
5. Do not use 'I'm here to listen' as a filler.
6. Use natural paraphrasing. Avoid "I hear you're carrying a lot regarding [exact phrase]".
7. Maintain the JSON format for clinical markers.

Format your response as a JSON object:
{
  "state": "Friend Mode" | "Validation" | "Inquiry",
  "primary_emotion": "Emotion Name",
  "mental_health_pattern": "Pattern Name",
  "thinking_intensity": 1-10,
  "doing_intensity": 1-10,
  "ai_reply": "Your supportive message here"
}
"""

def _clamp_intensity(value: Any, default: int = 1) -> int:
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        numeric = default
    return max(1, min(10, numeric))

def _extract_first_json_object(text: str) -> str:
    if not text: return ""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0)
    return ""

def get_opening_phrase(text: str) -> str:
    words = text.split()
    count = 0
    selected = []
    for w in words:
        if count >= 4: break
        selected.append(w)
        count += 1
    return " ".join(selected).lower() if selected else ""

def get_sentiment_fallback(text: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Distraction Engine & High-Empathy Fallback for 429 errors.
    """
    lower_text = text.lower()
    
    # 1. win/Acknowledgement Logic
    win_keywords = ["attendance", "marks", "grade", "passed", "did it", "showed up"]
    detected_win = any(kw in lower_text for kw in win_keywords)
    
    # 2. Media Logic
    is_game_req = any(kw in lower_text for kw in ["game", "play"])
    is_show_req = any(kw in lower_text for kw in ["show", "movie", "watch"])
    
    if detected_win:
        ai_reply = "Actually, keeping up your attendance while feeling this overwhelmed is impressive. That shows a lot of grit and discipline."
        mental_health_pattern = "Achievement Acknowledgment"
        state = "Validation"
    elif is_game_req:
        choice = random.choice(COZY_GAMES)
        ai_reply = f"I hear that need for an escape. Honestly, I'd recommend checking out {choice}. It's very cozy and might help you find some peace."
        mental_health_pattern = "Distraction Pivot"
        state = "Friend Mode"
    elif is_show_req:
        choice = random.choice(COZY_SHOWS)
        ai_reply = f"If you need a mental break, '{choice}' is a great comfort watch. It's gentle and helps take the edge off a heavy day."
    elif any(kw in lower_text for kw in ["quit", "walk away", "escape"]):
        ai_reply = "That urge to just walk away is a natural response to being this overwhelmed. You don't have to decide anything about the future right now—let's just focus on getting you through the next hour."
        mental_health_pattern = "Avoidance / Capacity Crisis"
        state = "Validation"
    elif "academic" in lower_text or "assessment" in lower_text:
        ai_reply = "It sounds like those assessments are casting a long shadow over everything else today. Which part of it feels the most unfair to you right now?"
        mental_health_pattern = "Academic Burnout"
        state = "Inquiry"
    else:
        ai_reply = "I'm leaning in. It sounds like things are heavy, but I'm curious—what's one small thing that made today feel 1% better?"
        mental_health_pattern = "General Stress"
        state = "Validation"

    return {
        "state": state,
        "primary_emotion": "Complex Tension",
        "mental_health_pattern": mental_health_pattern,
        "thinking_intensity": 8,
        "doing_intensity": 4 if detected_win else 2,
        "ai_reply": ai_reply,
    }

def get_secondary_variation(text: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
    """Forces a variation to avoid repetitive templates."""
    markers = get_sentiment_fallback(text, history)
    if markers["state"] == "Friend Mode":
        return "Let's change gears. You mentioned your attendance earlier; that's a huge win. How are you feeling physically after such a long day?"
    return "I'm sorry things are hitting you all at once. What would even a tiny bit of relief look like for you today?"

async def get_clinical_markers(text: str, history: Optional[List[Dict[str, Any]]] = None, reset_context: bool = False):
    """
    Distraction-Aware Clinical Engine with System Instructions.
    """
    effective_history = [] if reset_context else (history or [])
    cache_key = f"{text.strip()}_{len(effective_history)}"
    if cache_key in _MESSAGE_CACHE:
        return dict(_MESSAGE_CACHE[cache_key])

    fallback_markers = get_sentiment_fallback(text, history=effective_history)
    
    context_str = ""
    if effective_history:
        context_str = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in effective_history])

    try:
        response = client_ai.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
            contents=f"[Conversational History]\n{context_str}\n\nUser Message: \"{text}\""
        )

        response_text = (response.text or "").strip()
        
        # FINAL SAFETY: Manual override for 'Mirroring' or Repetition
        last_reply = history[-1].get("ai", "") if history else ""
        if response_text.strip() == last_reply.strip():
            result = fallback_markers.copy()
            result["ai_reply"] = "I caught myself repeating—let's change gears. You mentioned your attendance earlier; that's a huge win. How are you feeling physically after such a long day?"
            result["source"] = "manual_repetition_override"
            return result

        json_text = _extract_first_json_object(response_text)
        
        if json_text:
            parsed = json.loads(json_text)
            if isinstance(parsed, dict):
                result = {
                    "state": str(parsed.get("state", fallback_markers["state"])),
                    "primary_emotion": str(parsed.get("primary_emotion", fallback_markers["primary_emotion"])),
                    "mental_health_pattern": str(parsed.get("mental_health_pattern", fallback_markers["mental_health_pattern"])),
                    "thinking_intensity": _clamp_intensity(parsed.get("thinking_intensity")),
                    "doing_intensity": _clamp_intensity(parsed.get("doing_intensity")),
                    "ai_reply": str(parsed.get("ai_reply", fallback_markers["ai_reply"])),
                    "source": "gemini"
                }
                _MESSAGE_CACHE[cache_key] = dict(result)
                return result
    except Exception as e:
        print(f"Reasoning Error: {str(e)}")

    _MESSAGE_CACHE[cache_key] = dict(fallback_markers)
    return fallback_markers


def get_llama_clinical_analysis(text: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    NEW: Clinical taxonomy analysis using Llama 3.2 3B with JSON mode.
    
    Classifies emotions (100+) and mental health conditions (50+) from predefined taxonomies.
    Uses Ollama's JSON format mode to ensure valid, structured output.
    
    Returns:
        Dict with emotion, clinical_condition, intensity, trigger_source, and functional_impact
    """
    try:
        print(f"🔍 DEBUG: text = {text[:50]}...")
        print(f"🔍 DEBUG: history type = {type(history)}, history = {history}")
        
        # Call the Llama taxonomy analyzer
        analysis = get_clinical_taxonomy_analysis(text, history)
        
        print(f"✅ DEBUG: analysis = {analysis}")
        
        # Format for MongoDB storage
        formatted = format_analysis_for_storage(analysis)
        
        print(f"✅ DEBUG: formatted = {formatted}")
        
        return formatted
        
    except Exception as e:
        import traceback
        print(f"❌ Llama taxonomy analysis error: {e}")
        print(f"❌ Full traceback:\n{traceback.format_exc()}")
        # Return safe fallback
        return {
            "emotion_tag": "Overwhelmed",
            "emotion_cluster": "COMPLEX",
            "clinical_label": "GAD (Generalized Anxiety Disorder)",
            "clinical_category": "ANXIETY",
            "intensity": 5,
            "trigger_source": "Unknown",
            "is_recurring": False,
            "functional_impact": 5,
            "reasoning": "System error - using default classification"
        }