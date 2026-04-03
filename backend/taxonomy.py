"""
Clinical Taxonomy Module
100+ Nuanced Emotions and 50+ Mental Health Conditions
Used by Llama 3.2 3B to ensure consistent classification
"""

# ============================================================================
# EMOTION TAXONOMY (100+ NUANCED EMOTIONS)
# ============================================================================

EMOTION_CLUSTERS = {
    "JOY": [
        "Ecstatic", "Elated", "Serene", "Radiant", "Jubilant", "Blissful",
        "Peaceful", "Grateful", "Hopeful", "Content", "Cheerful", "Delighted",
        "Uplifted", "Optimistic", "Accomplished", "Proud", "Confident", "Energized",
        "Inspired", "Joyful", "Lighthearted", "Relieved", "Satisfied", "Thrilled"
    ],
    "SADNESS": [
        "Dejected", "Anguished", "Crushed", "Dismal", "Forlorn", "Despondent",
        "Melancholic", "Sorrowful", "Devastated", "Hopeless", "Downhearted", "Gloomy",
        "Miserable", "Depressed", "Blue", "Tearful", "Heartbroken", "Bereft",
        "Desolate", "Mournful", "Wistful", "Lonesome", "Dispirited", "Doleful"
    ],
    "ANGER": [
        "Infuriated", "Resentful", "Bitter", "Indignant", "Aggravated", "Furious",
        "Enraged", "Hostile", "Livid", "Irate", "Seething", "Exasperated",
        "Annoyed", "Irritated", "Vexed", "Frustrated", "Cross", "Wrathful",
        "Incensed", "Outraged", "Embittered", "Scornful", "Contemptuous", "Hostile"
    ],
    "FEAR": [
        "Petrified", "Apprehensive", "Frazzled", "Vulnerable", "Overwhelmed",
        "Anxious", "Panicked", "Terrified", "Dreadful", "Uneasy", "Alarmed",
        "Frightened", "Worried", "Nervous", "Jittery", "Skittish", "Tense",
        "Hypervigilant", "Paranoid", "Unsettled", "Trembling", "Spooked", "Startled",
        "Restless", "Distraught", "Shaken", "Aghast"
    ],
    "SHAME": [
        "Mortified", "Inadequate", "Chagrined", "Self-conscious", "Worthless",
        "Humiliated", "Degraded", "Ashamed", "Embarrassed", "Foolish", "Disgraced",
        "Inferior", "Deficient", "Unworthy", "Abashed", "Shamed", "Discomfited",
        "Disreputable", "Sullied", "Tainted", "Disparaged", "Demeaned", "Belittled"
    ],
    "COMPLEX": [
        "Ambivalent", "Nostalgic", "Apathetic", "Alienated", "Disconnected",
        "Cynical", "Numb", "Torn", "Conflicted", "Restless", "Detached",
        "Disenchanted", "Paralyzed", "Stuck", "Trapped", "Helpless", "Powerless",
        "Resigned", "Defeated", "Overwhelmed", "Scattered", "Confused", "Disoriented"
    ]
}

# Flattened list for easier lookups
ALL_EMOTIONS = []
for cluster, emotions in EMOTION_CLUSTERS.items():
    ALL_EMOTIONS.extend(emotions)

# ============================================================================
# MENTAL HEALTH CONDITIONS TAXONOMY (50+ CONDITIONS)
# ============================================================================

MENTAL_HEALTH_CONDITIONS = {
    "ANXIETY": [
        "GAD (Generalized Anxiety Disorder)",
        "Panic Disorder",
        "Agoraphobia",
        "Social Anxiety Disorder",
        "OCD (Obsessive-Compulsive Disorder)",
        "Health Anxiety (Illness Anxiety)",
        "Performance Anxiety"
    ],
    "MOOD": [
        "MDD (Major Depressive Disorder)",
        "Bipolar I Disorder",
        "Bipolar II Disorder",
        "Cyclothymia (Cyclothymic Disorder)",
        "Dysthymia (Persistent Depressive Disorder)",
        "Seasonal Affective Disorder (SAD)",
        "Premenstrual Dysphoric Disorder"
    ],
    "TRAUMA": [
        "PTSD (Post-Traumatic Stress Disorder)",
        "C-PTSD (Complex PTSD)",
        "Adjustment Disorder",
        "Acute Stress Disorder",
        "Trauma Response (General)",
        "Flashbacks/Intrusive Memories",
        "Hypervigilance"
    ],
    "IDENTITY_PERSONALITY": [
        "BPD (Borderline Personality Disorder)",
        "NPD (Narcissistic Personality Disorder)",
        "Avoidant Personality Disorder",
        "Dependent Personality Disorder",
        "Obsessive-Compulsive Personality Disorder",
        "Histrionic Personality Disorder",
        "Perfectionism (Maladaptive)"
    ],
    "COGNITIVE_NEURODEVELOPMENTAL": [
        "ADHD (Attention-Deficit/Hyperactivity Disorder)",
        "Insomnia (Sleep Disorder)",
        "Dissociation",
        "Depersonalization/Derealization",
        "Somatic Symptom Disorder",
        "Chronic Fatigue",
        "Executive Dysfunction"
    ],
    "SUBSTANCE_BEHAVIORAL": [
        "Substance Use Disorder (General)",
        "Alcohol Addiction",
        "Drug Addiction",
        "Gambling Addiction",
        "Internet/Gaming Addiction",
        "Withdrawal Symptoms",
        "Tolerance Development"
    ],
    "RELATIONAL_SOCIAL": [
        "Abandonment Fear",
        "Codependency",
        "Relationship Conflict",
        "Attachment Issues",
        "Loneliness",
        "Social Isolation",
        "Rejection Sensitivity"
    ],
    "EATING_BODY": [
        "Anorexia Nervosa",
        "Bulimia Nervosa",
        "Binge Eating Disorder",
        "Orthorexia",
        "Body Dysmorphic Disorder",
        "Eating Disorder (Other)"
    ],
    "GRIEF_LOSS": [
        "Grief (Acute)",
        "Grief (Prolonged)",
        "Complicated Grief",
        "Bereavement",
        "Anticipatory Grief"
    ]
}

# Flattened list for easier lookups
ALL_MENTAL_HEALTH_CONDITIONS = []
for category, conditions in MENTAL_HEALTH_CONDITIONS.items():
    ALL_MENTAL_HEALTH_CONDITIONS.extend(conditions)

# ============================================================================
# TRIGGER SOURCES
# ============================================================================

TRIGGER_SOURCES = [
    "Work/Career/Performance",
    "Relationships/Family",
    "Self-Image/Body Image",
    "Past Trauma/Memories",
    "Health/Medical Concerns",
    "Financial Stress",
    "Social Situations",
    "Loss/Grief",
    "Academic/Learning",
    "Loneliness/Isolation",
    "Uncertainty/Future",
    "Internal (No Clear Trigger)",
    "Environmental/Situational"
]

# ============================================================================
# TAXONOMY VALIDATION HELPERS
# ============================================================================

def validate_emotion(emotion: str) -> bool:
    """Check if emotion is in the taxonomy"""
    return emotion in ALL_EMOTIONS

def validate_condition(condition: str) -> bool:
    """Check if mental health condition is in the taxonomy"""
    return condition in ALL_MENTAL_HEALTH_CONDITIONS

def get_emotion_cluster(emotion: str) -> str:
    """Get the cluster for a given emotion"""
    for cluster, emotions in EMOTION_CLUSTERS.items():
        if emotion in emotions:
            return cluster
    return "COMPLEX"

def get_condition_category(condition: str) -> str:
    """Get the category for a given condition"""
    for category, conditions in MENTAL_HEALTH_CONDITIONS.items():
        if condition in conditions:
            return category
    return "OTHER"

def find_closest_emotion(emotion_text: str) -> str:
    """
    Tries to find the closest matching emotion from taxonomy.
    Uses simple string matching as fallback.
    """
    emotion_lower = emotion_text.lower()
    
    # Exact match (case-insensitive)
    for emotion in ALL_EMOTIONS:
        if emotion.lower() == emotion_lower:
            return emotion
    
    # Partial match
    for emotion in ALL_EMOTIONS:
        if emotion_lower in emotion.lower() or emotion.lower() in emotion_lower:
            return emotion
    
    # Default fallback
    return "Overwhelmed"  # Safe default

def find_closest_condition(condition_text: str) -> str:
    """
    Tries to find the closest matching condition from taxonomy.
    Uses simple string matching as fallback.
    """
    condition_lower = condition_text.lower()
    
    # Exact match (case-insensitive)
    for condition in ALL_MENTAL_HEALTH_CONDITIONS:
        if condition.lower() == condition_lower:
            return condition
    
    # Partial match
    for condition in ALL_MENTAL_HEALTH_CONDITIONS:
        if condition_lower in condition.lower() or condition.lower() in condition_lower:
            return condition
    
    # Default fallback
    return "GAD (Generalized Anxiety Disorder)"  # Safe default

# ============================================================================
# TAXONOMY STRING FOR PROMPTS
# ============================================================================

def get_emotion_taxonomy_string() -> str:
    """Returns formatted emotion taxonomy for prompts"""
    lines = ["EMOTION TAXONOMY (100+ emotions):"]
    for cluster, emotions in EMOTION_CLUSTERS.items():
        emotion_list = ", ".join(emotions)
        lines.append(f"  {cluster}: [{emotion_list}]")
    return "\n".join(lines)

def get_condition_taxonomy_string() -> str:
    """Returns formatted mental health condition taxonomy for prompts"""
    lines = ["MENTAL HEALTH CONDITIONS (50+ conditions):"]
    for category, conditions in MENTAL_HEALTH_CONDITIONS.items():
        condition_list = ", ".join(conditions)
        lines.append(f"  {category}: [{condition_list}]")
    return "\n".join(lines)

def get_full_taxonomy_string() -> str:
    """Returns complete taxonomy for system prompts"""
    return f"""{get_emotion_taxonomy_string()}

{get_condition_taxonomy_string()}

TRIGGER SOURCES: {', '.join(TRIGGER_SOURCES)}"""
