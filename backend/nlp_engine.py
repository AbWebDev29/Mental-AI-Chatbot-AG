import spacy
import asyncio
from database import connect_to_mongo, save_session_data, db

# Load the model
try:
    nlp = spacy.load("en_core_web_md")
except:
    # Fallback if md isn't installed
    nlp = spacy.load("en_core_web_sm")

async def get_clinical_markers(text: str):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Differential Logic: Thinking vs. Doing
            doc = nlp(text.lower())
            
            thinking_verbs = {"think", "wonder", "ponder", "imagine", "thought", "loop", "worry"}
            doing_verbs = {"did", "started", "finished", "worked", "moved", "action", "completed"}
            
            thinking_score = sum(1 for token in doc if token.lemma_ in thinking_verbs)
            doing_score = sum(1 for token in doc if token.lemma_ in doing_verbs)
            
            # Sentiment cues (fallback to help cases like "i feel super")
            positive_cues = {"super", "great", "amazing", "good", "happy", "fantastic", "awesome", "calm"}
            negative_cues = {"sad", "anxious", "depressed", "angry", "upset", "worried", "afraid", "stressed"}
            has_positive = any(tok in positive_cues for tok in text.lower().split())
            has_negative = any(tok in negative_cues for tok in text.lower().split())

            # Categorization based on your theory
            primary_state = "Neutral"
            if thinking_score > doing_score:
                primary_state = "Overthinking / Rumination"
            elif "later" in text or "tomorrow" in text:
                primary_state = "Procrastination"
            elif has_positive and not has_negative:
                primary_state = "Positive"
                thinking_score = max(thinking_score, 1)
                doing_score = max(doing_score, 1)
            elif has_negative and not has_positive:
                primary_state = "Needs Support"
                thinking_score = max(thinking_score, 2)
                doing_score = max(doing_score, 1)

            return {
                "state": primary_state,
                "thinking_intensity": thinking_score,
                "doing_intensity": doing_score,
                "tokens": [token.text for token in doc if not token.is_stop]
            }
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 5  # Wait 5, 10, then 15 seconds
                print(f"⚠️ Quota hit. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ Error in get_clinical_markers: {str(e)}")
                raise e
    
    # Fallback if all retries fail
    print("⚠️ Failed to get clinical markers after retries. Using fallback.")
    return {"state": "Analysis Pending", "thinking_intensity": 0, "doing_intensity": 0}