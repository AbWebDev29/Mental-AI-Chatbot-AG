"""
MONGODB DOCUMENT EXAMPLES

These show exactly what documents will look like after integrating the taxonomy system.
"""

# ============================================================================
# EXAMPLE 1: OCD with Compulsive Checking
# ============================================================================

OCD_CHECKING = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T10:30:00Z",
    "message": "I can't stop checking if the door is locked. I know I locked it but I have to check again and again.",
    "ai_reply": "It sounds like you're experiencing intrusive thoughts that won't leave you alone. Those repetitive urges to check are really distressing, and it makes sense that you'd feel trapped by them. Have you noticed if certain times of day make it worse?",
    "clinical_markers": {
        "emotion_tag": "Hypervigilant",
        "emotion_cluster": "FEAR",
        "clinical_label": "OCD (Obsessive-Compulsive Disorder)",
        "clinical_category": "ANXIETY",
        "intensity": 8,
        "trigger_source": "Internal (No Clear Trigger)",
        "is_recurring": True,
        "functional_impact": 7,
        "reasoning": "Repetitive checking behavior with compulsions indicating OCD pattern"
    }
}

# ============================================================================
# EXAMPLE 2: Perfectionism Leading to Paralysis
# ============================================================================

PERFECTIONISM = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T11:15:00Z",
    "message": "I feel like a complete failure at work. Everyone else is so much better than me. I can't submit my work until it's perfect.",
    "ai_reply": "That pressure to be perfect is exhausting, and I hear how it's blocking you from moving forward. The funny thing is, that high standard you set—the same thing that makes you thorough—is what's keeping you stuck. What would 'good enough' look like?",
    "clinical_markers": {
        "emotion_tag": "Paralyzed",
        "emotion_cluster": "COMPLEX",
        "clinical_label": "Perfectionism (Maladaptive)",
        "clinical_category": "IDENTITY_PERSONALITY",
        "intensity": 8,
        "trigger_source": "Work/Career/Performance",
        "is_recurring": True,
        "functional_impact": 8,
        "reasoning": "Performance perfectionism with functional paralysis and inadequacy"
    }
}

# ============================================================================
# EXAMPLE 3: PTSD with Flashbacks
# ============================================================================

PTSD_FLASHBACK = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T14:45:00Z",
    "message": "I'm having a flashback right now. I can see the accident happening again. I can't drive anymore because I'm too scared.",
    "ai_reply": "You're safe right now, and what you're experiencing is your nervous system reliving something terrifying. That's a trauma response, not reality. Let's ground you in this moment. Can you name 5 things you can see around you right now?",
    "clinical_markers": {
        "emotion_tag": "Petrified",
        "emotion_cluster": "FEAR",
        "clinical_label": "PTSD (Post-Traumatic Stress Disorder)",
        "clinical_category": "TRAUMA",
        "intensity": 9,
        "trigger_source": "Past Trauma/Memories",
        "is_recurring": True,
        "functional_impact": 9,
        "reasoning": "Acute flashback with severe functional impairment and high risk"
    }
}

# ============================================================================
# EXAMPLE 4: Social Anxiety with Avoidance
# ============================================================================

SOCIAL_ANXIETY = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T16:20:00Z",
    "message": "There's a work party tomorrow and I'm so nervous. I'm thinking about not going. Everyone will judge me.",
    "ai_reply": "That anticipatory anxiety is real, and avoidance feels safer in the moment but usually makes it worse. You've done this before—shown up when you were scared. What would help you get there tomorrow? Maybe going for just 30 minutes?",
    "clinical_markers": {
        "emotion_tag": "Apprehensive",
        "emotion_cluster": "FEAR",
        "clinical_label": "Social Anxiety Disorder",
        "clinical_category": "ANXIETY",
        "intensity": 7,
        "trigger_source": "Social Situations",
        "is_recurring": True,
        "functional_impact": 6,
        "reasoning": "Anticipatory social anxiety with avoidance behavior"
    }
}

# ============================================================================
# EXAMPLE 5: Depression with Hopelessness
# ============================================================================

DEPRESSION = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T20:00:00Z",
    "message": "I don't see the point in anything anymore. I don't want to get out of bed. Everything feels meaningless.",
    "ai_reply": "That hopelessness is a symptom, not a truth. Depression lies to us about how permanent things are. I'm concerned about your safety. Have you had thoughts of harming yourself? If yes, please reach out to a crisis line: 988.",
    "clinical_markers": {
        "emotion_tag": "Hopeless",
        "emotion_cluster": "SADNESS",
        "clinical_label": "MDD (Major Depressive Disorder)",
        "clinical_category": "MOOD",
        "intensity": 9,
        "trigger_source": "Internal (No Clear Trigger)",
        "is_recurring": True,
        "functional_impact": 9,
        "reasoning": "Severe depression with anhedonia and functional impairment. CRISIS RISK."
    }
}

# ============================================================================
# EXAMPLE 6: Anxiety with Panic Symptoms
# ============================================================================

PANIC_ATTACK = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-03T22:30:00Z",
    "message": "My heart is racing so fast. I can't catch my breath. I think I'm dying. I'm so scared right now.",
    "ai_reply": "You're having a panic attack. Your body is in fight-or-flight mode. You're not dying—your nervous system is overreacting. Let's slow your breathing. Breathe in for 4 counts, hold for 4, out for 4. Can you do that with me?",
    "clinical_markers": {
        "emotion_tag": "Panicked",
        "emotion_cluster": "FEAR",
        "clinical_label": "Panic Disorder",
        "clinical_category": "ANXIETY",
        "intensity": 9,
        "trigger_source": "Internal (No Clear Trigger)",
        "is_recurring": True,
        "functional_impact": 8,
        "reasoning": "Acute panic attack with somatic symptoms"
    }
}

# ============================================================================
# EXAMPLE 7: Abandonment Fear (BPD Pattern)
# ============================================================================

ABANDONMENT_FEAR = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-04T08:00:00Z",
    "message": "My friend didn't text me back yet and I'm sure they hate me. They probably never want to talk to me again. I'm so alone.",
    "ai_reply": "That fear of abandonment is really powerful, but it's your brain filling in gaps with worst-case scenarios. Your friend is probably just busy. Reaching out in fear vs. calmness usually gets different responses. How about you send a neutral check-in?",
    "clinical_markers": {
        "emotion_tag": "Anxious",
        "emotion_cluster": "FEAR",
        "clinical_label": "Abandonment Fear",
        "clinical_category": "RELATIONAL_SOCIAL",
        "intensity": 7,
        "trigger_source": "Relationships/Family",
        "is_recurring": True,
        "functional_impact": 6,
        "reasoning": "Rejection sensitivity with catastrophic thinking about relationships"
    }
}

# ============================================================================
# EXAMPLE 8: Dissociation/Derealization
# ============================================================================

DISSOCIATION = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-04T09:30:00Z",
    "message": "I feel disconnected from everything right now. Like I'm watching myself from outside my body. Nothing feels real. I'm terrified.",
    "ai_reply": "That's dissociation—your mind's way of protecting itself from overwhelming feelings. You're safe. Your mind is just retreating to cope. Let's ground you: Tell me about your 5 senses. What do you see, hear, smell, taste, feel?",
    "clinical_markers": {
        "emotion_tag": "Detached",
        "emotion_cluster": "COMPLEX",
        "clinical_label": "Dissociation",
        "clinical_category": "COGNITIVE_NEURODEVELOPMENTAL",
        "intensity": 8,
        "trigger_source": "Stress/Overwhelm",
        "is_recurring": True,
        "functional_impact": 7,
        "reasoning": "Depersonalization with fear response to dissociative symptoms"
    }
}

# ============================================================================
# EXAMPLE 9: Grief/Loss
# ============================================================================

GRIEF = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-04T11:00:00Z",
    "message": "It's been 2 months since they passed and I still can't believe they're gone. Everything reminds me of them. I miss them so much.",
    "ai_reply": "That's grief—the price of love. There's no timeline for this. Those reminders are hard right now, but someday they'll bring comfort. Have you had support around this loss? A grief group can really help.",
    "clinical_markers": {
        "emotion_tag": "Sorrowful",
        "emotion_cluster": "SADNESS",
        "clinical_label": "Grief (Acute)",
        "clinical_category": "GRIEF_LOSS",
        "intensity": 8,
        "trigger_source": "Loss/Grief",
        "is_recurring": True,
        "functional_impact": 5,
        "reasoning": "Acute grief response with waves of overwhelming sadness"
    }
}

# ============================================================================
# EXAMPLE 10: Positive Progress/Achievement
# ============================================================================

POSITIVE_ACHIEVEMENT = {
    "_id": "ObjectId(...)",
    "user_id": "user_123",
    "timestamp": "2026-04-04T13:00:00Z",
    "message": "I did it! I submitted my presentation even though it wasn't perfect. Everyone loved it. I feel so proud!",
    "ai_reply": "YES! That's huge! You pushed through the perfectionism and did the thing anyway. That took real courage. This is the kind of evidence that challenges that inner voice telling you that you're not good enough. How are you feeling now?",
    "clinical_markers": {
        "emotion_tag": "Proud",
        "emotion_cluster": "JOY",
        "clinical_label": "Achievement/No Clinical Concern",
        "clinical_category": "POSITIVE",
        "intensity": 2,
        "trigger_source": "Achievement",
        "is_recurring": False,
        "functional_impact": 1,
        "reasoning": "Positive achievement milestone with improved self-efficacy"
    }
}

# ============================================================================
# AGGREGATION EXAMPLES - WHAT YOU CAN DO WITH THIS DATA
# ============================================================================

MONGODB_AGGREGATIONS = """
# 1. MONTHLY EMOTION REPORT
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-04")}}},
    {$group: {
        _id: "$clinical_markers.emotion_tag",
        frequency: {$sum: 1},
        avg_intensity: {$avg: "$clinical_markers.intensity"}
    }},
    {$sort: {frequency: -1}},
    {$limit: 10}
])

Result:
[
  {_id: "Anxious", frequency: 8, avg_intensity: 7.1},
  {_id: "Overwhelmed", frequency: 6, avg_intensity: 8.2},
  {_id: "Hopeless", frequency: 4, avg_intensity: 8.8},
  ...
]

# 2. CLINICAL CONDITION TRENDS
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-04")}}},
    {$group: {
        _id: "$clinical_markers.clinical_label",
        occurrences: {$sum: 1},
        avg_intensity: {$avg: "$clinical_markers.intensity"},
        avg_functional_impact: {$avg: "$clinical_markers.functional_impact"}
    }},
    {$sort: {occurrences: -1}}
])

Result:
[
  {
    _id: "GAD (Generalized Anxiety Disorder)",
    occurrences: 12,
    avg_intensity: 7.3,
    avg_functional_impact: 6.8
  },
  {
    _id: "MDD (Major Depressive Disorder)",
    occurrences: 8,
    avg_intensity: 8.1,
    avg_functional_impact: 7.6
  },
  ...
]

# 3. CRISIS DETECTION (Last 24h)
db.sessions.find({
    "timestamp": {$gte: new Date(new Date() - 86400000)},
    "clinical_markers.intensity": {$gte: 9}
}).sort({timestamp: -1}).limit(10)

Result shows all high-intensity moments needing review

# 4. TRIGGER ANALYSIS
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-04")}}},
    {$group: {
        _id: "$clinical_markers.trigger_source",
        frequency: {$sum: 1},
        avg_intensity: {$avg: "$clinical_markers.intensity"}
    }},
    {$sort: {frequency: -1}}
])

Result shows: Work triggers 15 sessions, avg intensity 7.4
             Relationships trigger 8 sessions, avg intensity 8.1
             etc.

# 5. FUNCTIONAL IMPACT TREND (Is the user improving?)
db.sessions.aggregate([
    {$group: {
        _id: {$dateToString: {format: "%Y-%m-%d", date: "$timestamp"}},
        avg_impact: {$avg: "$clinical_markers.functional_impact"},
        session_count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
])

Result shows daily trend - if going down, user is improving!

# 6. RECURRING PATTERNS
db.sessions.aggregate([
    {$match: {"clinical_markers.is_recurring": true}},
    {$group: {
        _id: "$clinical_markers.clinical_label",
        times_identified: {$sum: 1}
    }},
    {$sort: {times_identified: -1}}
])

Result: Patterns that keep coming back (focus for treatment)

# 7. HIGH-RISK SESSIONS (For therapist review)
db.sessions.find({
    "clinical_markers.intensity": {$gte: 8},
    "clinical_markers.functional_impact": {$gte: 7}
}).sort({timestamp: -1})

# 8. EMOTION CLUSTER DISTRIBUTION
db.sessions.aggregate([
    {$match: {"timestamp": {$gte: ISODate("2026-03-04")}}},
    {$group: {
        _id: "$clinical_markers.emotion_cluster",
        frequency: {$sum: 1}
    }},
    {$sort: {frequency: -1}}
])

Result: JOY: 2%, SADNESS: 25%, ANGER: 15%, FEAR: 35%, SHAME: 10%, COMPLEX: 13%
"""

# ============================================================================
# REAL MONTHLY REPORT EXAMPLE
# ============================================================================

SAMPLE_MONTHLY_REPORT = {
    "user_id": "user_123",
    "month": "March 2026",
    "report_summary": {
        "total_sessions": 87,
        "avg_intensity": 7.2,
        "avg_functional_impact": 6.8,
        "primary_emotion": "Anxious",
        "primary_condition": "GAD (Generalized Anxiety Disorder)",
        "primary_trigger": "Work/Career/Performance"
    },
    "emotional_distribution": {
        "JOY": "3 sessions (3%)",
        "SADNESS": "18 sessions (21%)",
        "ANGER": "12 sessions (14%)",
        "FEAR": "35 sessions (40%)",
        "SHAME": "8 sessions (9%)",
        "COMPLEX": "11 sessions (13%)"
    },
    "top_conditions": [
        "GAD (Generalized Anxiety Disorder) - 22 sessions",
        "Perfectionism (Maladaptive) - 15 sessions",
        "Social Anxiety Disorder - 8 sessions",
        "OCD (Obsessive-Compulsive Disorder) - 6 sessions"
    ],
    "top_triggers": [
        "Work/Career/Performance - 28 sessions",
        "Social Situations - 12 sessions",
        "Relationships/Family - 10 sessions"
    ],
    "insight": "Your anxiety is primarily work-related and perfectionism-driven. March shows high intensity (avg 7.2) with significant functional impact. Consider focusing on workplace stress management.",
    "recommendation": "Cognitive Behavioral Therapy (CBT) for perfectionism would be beneficial. Try scheduling worry time (30 min/day) instead of checking throughout the day."
}

if __name__ == "__main__":
    print("MongoDB Document Examples")
    print("=" * 70)
    print("\nThese are real examples of what your database will contain")
    print("after implementing the taxonomy system.")
    print("\nEach document has:")
    print("  - emotion_tag (from 100+ emotions)")
    print("  - clinical_label (from 50+ conditions)")
    print("  - intensity (1-10)")
    print("  - functional_impact (1-10)")
    print("  - trigger_source (from 13 trigger types)")
    print("\nUse these fields for monthly reports, crisis detection, and trend analysis.")
