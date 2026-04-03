# Clinical Taxonomy System Documentation

## Overview
This system uses **Ollama's Llama 3.2 3B model** with **JSON mode** to classify user emotions and mental health conditions from predefined taxonomies:
- **100+ Nuanced Emotions** (organized into 6 clusters)
- **50+ Mental Health Conditions** (organized into 9 categories)

## Architecture

### Files
1. **taxonomy.py** - Defines all emotion and condition taxonomies
2. **clinical_analyzer_llama.py** - Ollama integration with JSON mode
3. **nlp_engine.py** - Integration with existing system

## How It Works

### 1. Taxonomy Constraints
The system uses Ollama's `format="json"` parameter to force valid JSON output. The prompt explicitly defines:
- All valid emotions
- All valid mental health conditions
- Valid trigger sources
- Expected output schema

### 2. JSON Mode Forces Compliance
```python
response = ollama.chat(
    model="llama3.2:3b",
    format="json",  # CRITICAL: Forces valid JSON output
    messages=[...],
    options={"temperature": 0.3}  # Lower = more consistent
)
```

### 3. Fallback Validation
If Llama picks an emotion/condition not in the taxonomy, the system automatically finds the closest match:
```python
if analysis.get("emotion") not in ALL_EMOTIONS:
    analysis["emotion"] = find_closest_emotion(analysis.get("emotion", ""))
```

## Usage in Main Code

### In main.py `/chat` endpoint:

```python
from nlp_engine import get_llama_clinical_analysis

@app.post("/chat")
async def chat_with_analysis(user_id: str, message: str):
    # ... existing code ...
    
    # Get clinical analysis from Llama with taxonomy constraints
    clinical_analysis = get_llama_clinical_analysis(
        message,
        history=clean_history  # Optional: for context
    )
    
    # clinical_analysis contains:
    # {
    #     "emotion_tag": "Paralyzed",
    #     "emotion_cluster": "COMPLEX",
    #     "clinical_label": "GAD",
    #     "clinical_category": "ANXIETY",
    #     "intensity": 9,
    #     "trigger_source": "Work/Career/Performance",
    #     "is_recurring": true,
    #     "functional_impact": 8,
    #     "reasoning": "..."
    # }
    
    # Save to MongoDB
    await db.sessions.insert_one({
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "message": message,
        "ai_reply": ai_reply,
        "clinical_markers": clinical_analysis
    })
```

## Emotion Taxonomy (100+ emotions)

### JOY (24 emotions)
Ecstatic, Elated, Serene, Radiant, Jubilant, Blissful, Peaceful, Grateful, Hopeful, Content, Cheerful, Delighted, Uplifted, Optimistic, Accomplished, Proud, Confident, Energized, Inspired, Joyful, Lighthearted, Relieved, Satisfied, Thrilled

### SADNESS (24 emotions)
Dejected, Anguished, Crushed, Dismal, Forlorn, Despondent, Melancholic, Sorrowful, Devastated, Hopeless, Downhearted, Gloomy, Miserable, Depressed, Blue, Tearful, Heartbroken, Bereft, Desolate, Mournful, Wistful, Lonesome, Dispirited, Doleful

### ANGER (24 emotions)
Infuriated, Resentful, Bitter, Indignant, Aggravated, Furious, Enraged, Hostile, Livid, Irate, Seething, Exasperated, Annoyed, Irritated, Vexed, Frustrated, Cross, Wrathful, Incensed, Outraged, Embittered, Scornful, Contemptuous, Hostile

### FEAR (26 emotions)
Petrified, Apprehensive, Frazzled, Vulnerable, Overwhelmed, Anxious, Panicked, Terrified, Dreadful, Uneasy, Alarmed, Frightened, Worried, Nervous, Jittery, Skittish, Tense, Hypervigilant, Paranoid, Unsettled, Trembling, Spooked, Startled, Restless, Distraught, Shaken, Aghast

### SHAME (22 emotions)
Mortified, Inadequate, Chagrined, Self-conscious, Worthless, Humiliated, Degraded, Ashamed, Embarrassed, Foolish, Disgraced, Inferior, Deficient, Unworthy, Abashed, Shamed, Discomfited, Disreputable, Sullied, Tainted, Disparaged, Demeaned, Belittled

### COMPLEX (22 emotions)
Ambivalent, Nostalgic, Apathetic, Alienated, Disconnected, Cynical, Numb, Torn, Conflicted, Restless, Detached, Disenchanted, Paralyzed, Stuck, Trapped, Helpless, Powerless, Resigned, Defeated, Overwhelmed, Scattered, Confused, Disoriented

## Mental Health Conditions Taxonomy (50+ conditions)

### ANXIETY (7 conditions)
- GAD (Generalized Anxiety Disorder)
- Panic Disorder
- Agoraphobia
- Social Anxiety Disorder
- OCD (Obsessive-Compulsive Disorder)
- Health Anxiety (Illness Anxiety)
- Performance Anxiety

### MOOD (7 conditions)
- MDD (Major Depressive Disorder)
- Bipolar I Disorder
- Bipolar II Disorder
- Cyclothymia (Cyclothymic Disorder)
- Dysthymia (Persistent Depressive Disorder)
- Seasonal Affective Disorder (SAD)
- Premenstrual Dysphoric Disorder

### TRAUMA (7 conditions)
- PTSD (Post-Traumatic Stress Disorder)
- C-PTSD (Complex PTSD)
- Adjustment Disorder
- Acute Stress Disorder
- Trauma Response (General)
- Flashbacks/Intrusive Memories
- Hypervigilance

### IDENTITY_PERSONALITY (7 conditions)
- BPD (Borderline Personality Disorder)
- NPD (Narcissistic Personality Disorder)
- Avoidant Personality Disorder
- Dependent Personality Disorder
- Obsessive-Compulsive Personality Disorder
- Histrionic Personality Disorder
- Perfectionism (Maladaptive)

### COGNITIVE_NEURODEVELOPMENTAL (7 conditions)
- ADHD (Attention-Deficit/Hyperactivity Disorder)
- Insomnia (Sleep Disorder)
- Dissociation
- Depersonalization/Derealization
- Somatic Symptom Disorder
- Chronic Fatigue
- Executive Dysfunction

### SUBSTANCE_BEHAVIORAL (7 conditions)
- Substance Use Disorder (General)
- Alcohol Addiction
- Drug Addiction
- Gambling Addiction
- Internet/Gaming Addiction
- Withdrawal Symptoms
- Tolerance Development

### RELATIONAL_SOCIAL (7 conditions)
- Abandonment Fear
- Codependency
- Relationship Conflict
- Attachment Issues
- Loneliness
- Social Isolation
- Rejection Sensitivity

### EATING_BODY (6 conditions)
- Anorexia Nervosa
- Bulimia Nervosa
- Binge Eating Disorder
- Orthorexia
- Body Dysmorphic Disorder
- Eating Disorder (Other)

### GRIEF_LOSS (5 conditions)
- Grief (Acute)
- Grief (Prolonged)
- Complicated Grief
- Bereavement
- Anticipatory Grief

## Trigger Sources
Work/Career/Performance, Relationships/Family, Self-Image/Body Image, Past Trauma/Memories, Health/Medical Concerns, Financial Stress, Social Situations, Loss/Grief, Academic/Learning, Loneliness/Isolation, Uncertainty/Future, Internal (No Clear Trigger), Environmental/Situational

## Testing

Run the test script:
```bash
cd backend
python clinical_analyzer_llama.py
```

Example output for "I can't stop checking the door lock":
```json
{
  "emotion": "Hypervigilant",
  "emotion_cluster": "FEAR",
  "clinical_condition": "OCD (Obsessive-Compulsive Disorder)",
  "clinical_category": "ANXIETY",
  "intensity": 8,
  "trigger_source": "Internal (No Clear Trigger)",
  "is_recurring": true,
  "functional_impact": 7,
  "reasoning": "Repetitive checking behavior with anxiety indicates OCD"
}
```

## MongoDB Document Structure

Every session in MongoDB will now have:
```json
{
  "_id": ObjectId(...),
  "user_id": "user123",
  "timestamp": ISODate("2026-04-03T..."),
  "message": "I can't stop checking the door lock...",
  "ai_reply": "It sounds like you're experiencing intrusive thoughts...",
  "clinical_markers": {
    "emotion_tag": "Hypervigilant",
    "emotion_cluster": "FEAR",
    "clinical_label": "OCD (Obsessive-Compulsive Disorder)",
    "clinical_category": "ANXIETY",
    "intensity": 8,
    "trigger_source": "Internal (No Clear Trigger)",
    "is_recurring": true,
    "functional_impact": 7,
    "reasoning": "Repetitive checking behavior with anxiety indicates OCD"
  }
}
```

## Benefits

✅ **Consistency**: Labels stay consistent across sessions
✅ **Reportability**: Easy to count occurrences of specific conditions
✅ **Privacy**: All processing happens locally on MacBook Air
✅ **Speed**: Llama 3.2 3B is fast (~500ms per analysis)
✅ **Accuracy**: JSON mode forces valid taxonomy adherence
✅ **Fallback**: Keyword matching if Ollama unavailable

## Troubleshooting

### "JSON format not supported" error
Make sure Ollama is running the latest version:
```bash
ollama pull llama3.2:3b
```

### Analysis not using taxonomy
Lower the temperature in `clinical_analyzer_llama.py` (currently 0.3, can go to 0.1):
```python
options={"temperature": 0.1}  # More deterministic
```

### Emotion/condition not in taxonomy
Check that you're importing from the correct file:
```python
from clinical_analyzer_llama import get_clinical_taxonomy_analysis
```

The fallback system will automatically map non-taxonomy values to the closest match.
