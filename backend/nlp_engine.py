import spacy

# Load the model
try:
    nlp = spacy.load("en_core_web_md")
except:
    # Fallback if md isn't installed
    nlp = spacy.load("en_core_web_sm")

def get_clinical_markers(text: str):
    doc = nlp(text.lower())
    
    # Differential Logic: Thinking vs. Doing
    thinking_verbs = {"think", "wonder", "ponder", "imagine", "thought", "loop", "worry"}
    doing_verbs = {"did", "started", "finished", "worked", "moved", "action", "completed"}
    
    thinking_score = sum(1 for token in doc if token.lemma_ in thinking_verbs)
    doing_score = sum(1 for token in doc if token.lemma_ in doing_verbs)
    
    # Categorization based on your theory
    primary_state = "Neutral"
    if thinking_score > doing_score:
        primary_state = "Overthinking / Rumination"
    elif "later" in text or "tomorrow" in text:
        primary_state = "Procrastination"

    return {
        "state": primary_state,
        "thinking_intensity": thinking_score,
        "doing_intensity": doing_score,
        "tokens": [token.text for token in doc if not token.is_stop]
    }