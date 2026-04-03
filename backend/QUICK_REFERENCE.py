"""
QUICK REFERENCE: 100+ Emotions & 50+ Conditions Taxonomy

Use this for quick lookups. Full lists are in taxonomy.py
"""

# ============================================================================
# 100+ EMOTIONS AT A GLANCE
# ============================================================================

EMOTIONS_BY_CLUSTER = {
    "JOY": 24,           # Ecstatic, Elated, Serene, Radiant, Jubilant...
    "SADNESS": 24,       # Dejected, Anguished, Crushed, Dismal, Forlorn...
    "ANGER": 24,         # Infuriated, Resentful, Bitter, Indignant...
    "FEAR": 26,          # Petrified, Apprehensive, Frazzled, Vulnerable...
    "SHAME": 22,         # Mortified, Inadequate, Chagrined, Self-conscious...
    "COMPLEX": 22,       # Ambivalent, Nostalgic, Apathetic, Alienated...
}
# TOTAL: 138 emotions

# ============================================================================
# 50+ MENTAL HEALTH CONDITIONS AT A GLANCE
# ============================================================================

CONDITIONS_BY_CATEGORY = {
    "ANXIETY": 7,                           # GAD, Panic, OCD, Social Anxiety...
    "MOOD": 7,                              # MDD, Bipolar I/II, Dysthymia...
    "TRAUMA": 7,                            # PTSD, C-PTSD, Flashbacks...
    "IDENTITY_PERSONALITY": 7,              # BPD, NPD, Perfectionism...
    "COGNITIVE_NEURODEVELOPMENTAL": 7,      # ADHD, Insomnia, Dissociation...
    "SUBSTANCE_BEHAVIORAL": 7,              # Addiction, Withdrawal...
    "RELATIONAL_SOCIAL": 7,                 # Codependency, Abandonment Fear...
    "EATING_BODY": 6,                       # Anorexia, Bulimia, BDD...
    "GRIEF_LOSS": 5,                        # Grief, Bereavement...
}
# TOTAL: 60 conditions

# ============================================================================
# USAGE PATTERN: What you'll see in MongoDB
# ============================================================================

EXAMPLE_DOCUMENTS = {
    "Perfectionist": {
        "message": "I can't submit my work until it's perfect",
        "emotion_tag": "Paralyzed",
        "emotion_cluster": "COMPLEX",
        "clinical_label": "Perfectionism (Maladaptive)",
        "clinical_category": "IDENTITY_PERSONALITY",
        "intensity": 8,
        "trigger_source": "Work/Career/Performance",
        "is_recurring": True
    },
    
    "OCD Checking": {
        "message": "I keep checking if the door is locked",
        "emotion_tag": "Hypervigilant",
        "emotion_cluster": "FEAR",
        "clinical_label": "OCD (Obsessive-Compulsive Disorder)",
        "clinical_category": "ANXIETY",
        "intensity": 7,
        "trigger_source": "Internal (No Clear Trigger)",
        "is_recurring": True
    },
    
    "Trauma Response": {
        "message": "I'm having flashbacks of the accident",
        "emotion_tag": "Petrified",
        "emotion_cluster": "FEAR",
        "clinical_label": "PTSD (Post-Traumatic Stress Disorder)",
        "clinical_category": "TRAUMA",
        "intensity": 9,
        "trigger_source": "Past Trauma/Memories",
        "is_recurring": True
    },
    
    "Social Anxiety": {
        "message": "I'm too scared to go to the party",
        "emotion_tag": "Apprehensive",
        "emotion_cluster": "FEAR",
        "clinical_label": "Social Anxiety Disorder",
        "clinical_category": "ANXIETY",
        "intensity": 7,
        "trigger_source": "Social Situations",
        "is_recurring": True
    },
    
    "Depression": {
        "message": "I don't see the point in anything anymore",
        "emotion_tag": "Hopeless",
        "emotion_cluster": "SADNESS",
        "clinical_label": "MDD (Major Depressive Disorder)",
        "clinical_category": "MOOD",
        "intensity": 9,
        "trigger_source": "Internal (No Clear Trigger)",
        "is_recurring": True
    }
}

# ============================================================================
# TESTING PROMPTS: Try these to verify classification
# ============================================================================

TEST_MESSAGES = [
    # OCD Test
    ("I can't stop checking the door lock. I know I locked it but I have to check again.",
     "Should classify as: Hypervigilant, OCD"),
    
    # Perfectionism Test
    ("I feel like a complete failure at work. Everyone else is better than me.",
     "Should classify as: Inadequate, Perfectionism/GAD"),
    
    # Trauma Test
    ("I'm having flashbacks from the accident. I can't drive anymore.",
     "Should classify as: Petrified, PTSD"),
    
    # Achievement Test
    ("I felt so proud when I finished my presentation today!",
     "Should classify as: Proud, Not a mental health concern"),
    
    # Anxiety Test
    ("My heart is racing and I can't breathe. I feel like I'm dying.",
     "Should classify as: Panicked, Panic Disorder"),
    
    # Social Anxiety Test
    ("I'm too nervous to speak up in the meeting with my boss.",
     "Should classify as: Apprehensive, Social Anxiety"),
    
    # Depression Test
    ("Everything feels pointless. I don't want to get out of bed.",
     "Should classify as: Hopeless, MDD"),
    
    # Abandonment Fear Test
    ("My friend didn't text me back and I'm sure they hate me.",
     "Should classify as: Anxious, Abandonment Fear"),
    
    # Dissociation Test
    ("I feel disconnected from everything, like I'm watching myself from outside.",
     "Should classify as: Detached, Dissociation"),
    
    # Grief Test
    ("I can't stop thinking about my loss. Everything reminds me of them.",
     "Should classify as: Sorrowful, Grief/Bereavement")
]

# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

INTEGRATION_STEPS = """
☐ 1. Import get_llama_clinical_analysis in main.py
☐ 2. Add asyncio import to main.py
☐ 3. Update /chat endpoint to call get_llama_clinical_analysis
☐ 4. Test with: python clinical_analyzer_llama.py
☐ 5. Verify Ollama is running: ollama list
☐ 6. Check MongoDB for clinical_markers field
☐ 7. Run integration test: POST /chat?user_id=test&message=test
☐ 8. View results in MongoDB Compass
☐ 9. Build reporting queries on clinical_markers
☐ 10. Deploy to production
"""

# ============================================================================
# MONGODB QUERIES FOR ANALYSIS
# ============================================================================

USEFUL_QUERIES = """
# Most common emotions this month
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-03")}}},
    {$group: {_id: "$clinical_markers.emotion_tag", count: {$sum: 1}}},
    {$sort: {count: -1}},
    {$limit: 10}
])

# Most common conditions
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-03")}}},
    {$group: {_id: "$clinical_markers.clinical_label", count: {$sum: 1}}},
    {$sort: {count: -1}},
    {$limit: 5}
])

# High intensity sessions (9-10)
db.sessions.find({
    "clinical_markers.intensity": {$gte: 9},
    "timestamp": {$gte: ISODate("2026-03-03")}
}).sort({timestamp: -1}).limit(10)

# Recurring patterns
db.sessions.aggregate([
    {$match: {"clinical_markers.is_recurring": true}},
    {$group: {_id: "$clinical_markers.clinical_label", count: {$sum: 1}}},
    {$sort: {count: -1}}
])

# By trigger source
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-03")}}},
    {$group: {_id: "$clinical_markers.trigger_source", count: {$sum: 1}}},
    {$sort: {count: -1}}
])

# Functional impact over time
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-03")}}},
    {$group: {
        _id: {$dateToString: {format: "%Y-%m-%d", date: "$timestamp"}},
        avg_impact: {$avg: "$clinical_markers.functional_impact"}
    }},
    {$sort: {_id: 1}}
])
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

TROUBLESHOOTING = """
PROBLEM: "Module not found: clinical_analyzer_llama"
SOLUTION: Make sure you created clinical_analyzer_llama.py in backend/

PROBLEM: "JSON mode not supported"
SOLUTION: Ollama might be using old Llama model. Run:
  ollama pull llama3.2:3b

PROBLEM: "Connection refused" to Ollama
SOLUTION: Make sure Ollama is running:
  ollama serve

PROBLEM: Clinical analysis returning all default values
SOLUTION: Lower temperature (currently 0.3) for more consistent results:
  options={"temperature": 0.1}

PROBLEM: Emotion/condition not in taxonomy
SOLUTION: That's OK! The system automatically finds the closest match.
  Check taxonomy.py for all valid values.

PROBLEM: MongoDB save failing
SOLUTION: Make sure clinical_markers is included in insert:
  "clinical_markers": clinical_analysis

PROBLEM: Too slow (~3-5 seconds per analysis)
SOLUTION: Decrease context history or use asyncio.create_task() (already done)
"""

# ============================================================================
# WHAT'S NEXT
# ============================================================================

NEXT_STEPS = """
1. BUILD MONTHLY REPORTS
   - Aggregate emotions by week
   - Track trigger patterns
   - Measure functional impact trend

2. ADD CRISIS DETECTION
   - Flag high intensity + high functional impact
   - Alert if same crisis condition appears 3+ times

3. PERSONALIZED RECOMMENDATIONS
   - "You struggle with perfectionism, try: XYZ technique"
   - Link to specific therapy resources by condition

4. COMPARE TO NORMS
   - "Your anxiety level is higher than usual this week"
   - Show seasonal patterns

5. EXPORT REPORTS
   - PDF/CSV for therapist sharing
   - HIPAA-compliant data export
"""

if __name__ == "__main__":
    print("="*60)
    print("TAXONOMY SYSTEM REFERENCE")
    print("="*60)
    print(f"\nEmotions: {sum(EMOTIONS_BY_CLUSTER.values())} total")
    print(f"Conditions: {sum(CONDITIONS_BY_CATEGORY.values())} total")
    print(f"\nSee TAXONOMY_SYSTEM.md for full documentation")
    print(f"See INTEGRATION_EXAMPLE.md for code examples")
    print("="*60)
