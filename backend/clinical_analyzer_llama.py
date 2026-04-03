"""
Clinical Analysis Engine using Ollama with Taxonomy Constraints
Forces Llama 3.2 3B to classify emotions and mental health conditions
from predefined taxonomies using JSON mode for strict output.
"""

import json
import ollama
from typing import Dict, Any, Optional, List
from taxonomy import (
    get_full_taxonomy_string,
    find_closest_emotion,
    find_closest_condition,
    get_emotion_cluster,
    get_condition_category,
    ALL_EMOTIONS,
    ALL_MENTAL_HEALTH_CONDITIONS,
    TRIGGER_SOURCES
)


def get_clinical_taxonomy_analysis(
    user_input: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Uses Ollama's JSON mode with Llama 3.2 3B to classify:
    - Emotion (from 100+ list)
    - Mental Health Condition (from 50+ list)
    - Intensity (1-10)
    - Trigger source
    - Recurrence pattern
    
    Forces valid JSON output using format="json"
    """
    
    # Build context from history
    history_context = ""
    if chat_history and len(chat_history) > 0:
        history_context = "\nPrevious conversation:\n"
        for exchange in chat_history[-3:]:  # Last 3 exchanges
            history_context += f"User: {exchange.get('user_msg', '')}\n"
            history_context += f"AI: {exchange.get('ai_reply', '')}\n"
    
    # THE MASTER TAXONOMY PROMPT
    # This defines ALL the rules and valid options
    system_prompt = f"""
You are a Clinical NLP Classification System. Your role is to analyze the user's mental and emotional state and map it to a specific taxonomy.

CRITICAL RULES:
1. You MUST respond with ONLY valid JSON (no markdown, no explanation)
2. You MUST choose emotions ONLY from the provided emotion list
3. You MUST choose clinical conditions ONLY from the provided condition list
4. If an emotion/condition isn't an exact match, find the closest one from the lists
5. Intensity must be a number between 1-10
6. Provide clear, clinical reasoning

{get_full_taxonomy_string()}

CURRENT CONTEXT:
{history_context}

YOUR TASK:
Analyze the user's message and extract:
1. The most accurate emotion (from the 100+ list above)
2. The most relevant mental health condition (from the 50+ list above)
3. The emotion cluster (JOY, SADNESS, ANGER, FEAR, SHAME, COMPLEX)
4. The condition category (ANXIETY, MOOD, TRAUMA, etc.)
5. Intensity rating (1-10): How severe is their current distress?
6. Primary trigger source (from the list: {', '.join(TRIGGER_SOURCES)})
7. Is this a recurring pattern or new symptom? (boolean)
8. Functional impact (1-10): How much is this affecting their daily life?

RESPONSE SCHEMA (STRICT JSON ONLY):
{{
  "emotion": "string (MUST be from emotion list)",
  "emotion_cluster": "string (JOY/SADNESS/ANGER/FEAR/SHAME/COMPLEX)",
  "clinical_condition": "string (MUST be from condition list)",
  "condition_category": "string (ANXIETY/MOOD/TRAUMA/etc)",
  "intensity": number (1-10),
  "trigger_source": "string (from trigger sources list)",
  "is_recurring": boolean,
  "functional_impact": number (1-10),
  "reasoning": "string (brief 1-sentence explanation)"
}}

Remember: ONLY JSON output. NO other text.
"""

    user_message = f"Analyze this mental health statement: {user_input}"
    
    try:
        # Call Ollama with JSON mode ENABLED
        response = ollama.chat(
            model="llama3.2:3b",
            format="json",  # CRITICAL: Forces valid JSON output
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            options={
                "temperature": 0.3,  # Lower temperature = more consistent classifications
                "num_ctx": 4096
            }
        )
        
        # Extract and parse JSON
        response_text = response["message"]["content"].strip()
        
        # Clean up markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        analysis = json.loads(response_text)
        
        # VALIDATION & FALLBACK: Ensure values are from taxonomy
        # If Llama somehow picked something not in the list, find closest match
        if analysis.get("emotion") not in ALL_EMOTIONS:
            analysis["emotion"] = find_closest_emotion(analysis.get("emotion", ""))
        
        if analysis.get("clinical_condition") not in ALL_MENTAL_HEALTH_CONDITIONS:
            analysis["clinical_condition"] = find_closest_condition(analysis.get("clinical_condition", ""))
        
        # Update clusters/categories based on validated values
        analysis["emotion_cluster"] = get_emotion_cluster(analysis["emotion"])
        analysis["condition_category"] = get_condition_category(analysis["clinical_condition"])
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error from Ollama: {e}")
        # Return safe fallback
        return get_fallback_analysis(user_input)
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return get_fallback_analysis(user_input)


def get_fallback_analysis(user_input: str) -> Dict[str, Any]:
    """
    Fallback analysis when Ollama is unavailable or returns invalid JSON.
    Uses simple keyword matching against taxonomy.
    """
    lower_input = user_input.lower()
    
    # Simple keyword detection for fallback
    emotion = "Overwhelmed"  # Safe default
    condition = "GAD (Generalized Anxiety Disorder)"  # Safe default
    
    # Basic keyword matching
    if any(word in lower_input for word in ["happy", "great", "good", "wonderful", "fantastic"]):
        emotion = "Elated"
        condition = "Not Applicable"
    elif any(word in lower_input for word in ["sad", "down", "depressed", "miserable"]):
        emotion = "Dejected"
        condition = "MDD (Major Depressive Disorder)"
    elif any(word in lower_input for word in ["angry", "frustrated", "mad", "furious"]):
        emotion = "Infuriated"
        condition = "Anger Management Issue"
    elif any(word in lower_input for word in ["scared", "afraid", "panic", "terrified"]):
        emotion = "Petrified"
        condition = "Panic Disorder"
    elif any(word in lower_input for word in ["ashamed", "guilty", "embarrassed", "worthless"]):
        emotion = "Mortified"
        condition = "MDD (Major Depressive Disorder)"
    elif any(word in lower_input for word in ["flashback", "trauma", "ptsd"]):
        emotion = "Petrified"
        condition = "PTSD (Post-Traumatic Stress Disorder)"
    
    intensity = 5  # Default middle value
    if any(word in lower_input for word in ["very", "so", "extremely", "awful", "terrible"]):
        intensity = 8
    elif any(word in lower_input for word in ["slightly", "bit", "little", "somewhat"]):
        intensity = 3
    
    return {
        "emotion": emotion,
        "emotion_cluster": get_emotion_cluster(emotion),
        "clinical_condition": condition,
        "condition_category": get_condition_category(condition),
        "intensity": intensity,
        "trigger_source": "Unknown",
        "is_recurring": False,
        "functional_impact": intensity,
        "reasoning": "Fallback analysis due to system unavailability"
    }


def format_analysis_for_storage(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the clinical analysis for MongoDB storage.
    """
    return {
        "emotion_tag": analysis.get("emotion", "Unknown"),
        "emotion_cluster": analysis.get("emotion_cluster", "COMPLEX"),
        "clinical_label": analysis.get("clinical_condition", "Unclassified"),
        "clinical_category": analysis.get("condition_category", "OTHER"),
        "intensity": int(analysis.get("intensity", 5)),
        "trigger_source": analysis.get("trigger_source", "Unknown"),
        "is_recurring": bool(analysis.get("is_recurring", False)),
        "functional_impact": int(analysis.get("functional_impact", 5)),
        "reasoning": analysis.get("reasoning", "")
    }


def batch_analyze_history(
    messages: List[str],
    chat_history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, Any]]:
    """
    Analyzes multiple messages for trend analysis.
    Useful for generating monthly reports.
    """
    results = []
    for message in messages:
        analysis = get_clinical_taxonomy_analysis(message, chat_history)
        results.append(format_analysis_for_storage(analysis))
    return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test the system
    test_messages = [
        "I can't stop checking the door lock. I know I locked it but I have to check again.",
        "I feel like a complete failure at work. Everyone else is better than me.",
        "I'm having flashbacks from the accident. I can't drive anymore.",
        "I felt so proud when I finished my presentation today!"
    ]
    
    print("Testing Clinical Taxonomy Analysis...\n")
    for msg in test_messages:
        print(f"Input: {msg}")
        result = get_clinical_taxonomy_analysis(msg)
        print(f"Analysis: {json.dumps(result, indent=2)}\n")
