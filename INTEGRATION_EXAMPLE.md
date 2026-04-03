"""
INTEGRATION EXAMPLE: How to use the Llama Taxonomy Analysis in main.py

This file shows the exact code changes needed to integrate the new clinical analysis
into your existing chat endpoint.
"""

# ============================================================================
# STEP 1: Update imports at the top of main.py
# ============================================================================

# Add this import:
from nlp_engine import get_llama_clinical_analysis


# ============================================================================
# STEP 2: Update the /chat endpoint
# ============================================================================

# BEFORE: Your current /chat endpoint just saves basic markers
# AFTER: It now includes full taxonomy-based clinical analysis

async def chat_with_analysis_UPDATED(user_id: str = Query(...), message: str = Query(...)):
    """
    UPDATED chat endpoint with Llama taxonomy-based clinical analysis.
    
    Flow:
    1. Llama 3.2 generates empathetic response (immediate)
    2. Background: Llama taxonomy analysis classifies emotion/condition
    3. Background: Save to MongoDB with clinical markers
    """
    # === EXISTING CODE ===
    cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
    history_docs: List[Dict[str, Any]] = await cursor.to_list(length=5)
    
    last_responses = []
    for doc in history_docs:
        if len(last_responses) >= 2: 
            break
        last_responses.append(str(doc.get("ai_reply", "")))
    
    history_docs_reversed = list(reversed(history_docs))
    clean_history = [
        {
            "user": doc.get("message", ""), 
            "ai": doc.get("ai_reply", ""), 
            "markers": doc.get("clinical_markers", {})
        }
        for doc in history_docs_reversed
    ]
    
    context_from_history = "\n".join([
        f"User: {h['user']} AI: {h['ai']}" 
        for h in clean_history
    ])
    
    # Generate empathetic response (same as before)
    try:
        ai_reply = generate_llama_response(message, context_from_history)
    except Exception as e:
        print(f"Llama Error: {e}")
        ai_reply = "I'm here, but I'm having a little trouble thinking. Can we try that again?"
    
    # === NEW CODE: Check for repetition ===
    is_repeat = False
    hard_pivot_msg = ""
    
    for prev_reply in last_responses:
        ratio = difflib.SequenceMatcher(
            None, 
            ai_reply.lower(), 
            prev_reply.lower()
        ).ratio()
        
        if ai_reply.strip() == prev_reply.strip():
            print(f"🚨 EXACT MATCH DETECTED")
            hard_pivot_msg = "I want to make sure I'm truly listening. Let's set the usual talk aside—how are you actually breathing right now?"
            is_repeat = True
            break
        elif ratio > 0.95:
            print(f"⚠️ SEMANTIC MATCH (>95%)")
            hard_pivot_msg = "I want to make sure I'm not just repeating myself. How is your sleep holding up?"
            is_repeat = True
            break
    
    if is_repeat:
        ai_reply = hard_pivot_msg
    
    # === NEW CODE: Clinical taxonomy analysis (non-blocking) ===
    async def save_with_clinical_analysis(user_id: str, message: str, ai_reply: str):
        """Background task: analyze emotions/conditions and save to DB"""
        try:
            # Get the clinical analysis (100+ emotions, 50+ conditions)
            clinical_analysis = get_llama_clinical_analysis(
                message,
                history=[
                    {"user_msg": h["user"], "ai_reply": h["ai"]}
                    for h in clean_history
                ]
            )
            
            print(f"✅ Clinical analysis: {clinical_analysis.get('clinical_label')}")
            
            # Save full session with clinical markers to MongoDB
            await db.sessions.insert_one({
                "user_id": user_id,
                "timestamp": datetime.datetime.utcnow(),
                "message": message,
                "ai_reply": ai_reply,
                "clinical_markers": clinical_analysis
            })
            
        except Exception as e:
            print(f"⚠️ Background analysis error: {e}")
            # Fallback: save without full analysis
            try:
                await db.sessions.insert_one({
                    "user_id": user_id,
                    "timestamp": datetime.datetime.utcnow(),
                    "message": message,
                    "ai_reply": ai_reply,
                    "clinical_markers": {"status": "fallback"}
                })
            except Exception as e2:
                print(f"❌ Failed to save session: {e2}")
    
    # Fire off the background task (doesn't block user)
    asyncio.create_task(save_with_clinical_analysis(user_id, message, ai_reply))
    
    # === IMMEDIATE RESPONSE TO USER ===
    return {
        "reply": ai_reply,
        "status": "analyzing",
        "note": "Clinical analysis processing..."
    }


# ============================================================================
# STEP 3: Optional - Add a reporting endpoint
# ============================================================================

@app.get("/insights/{user_id}")
async def get_user_insights(user_id: str):
    """
    Returns a summary of the user's emotional and clinical patterns.
    """
    try:
        # Aggregate clinical markers from last 30 days
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": thirty_days_ago}
                }
            },
            {
                "$group": {
                    "_id": "$clinical_markers.emotional_tag",
                    "count": {"$sum": 1},
                    "avg_intensity": {"$avg": "$clinical_markers.intensity"}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 5
            }
        ]
        
        top_emotions = await db.sessions.aggregate(pipeline).to_list(None)
        
        # Clinical conditions pipeline
        pipeline_conditions = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": thirty_days_ago}
                }
            },
            {
                "$group": {
                    "_id": "$clinical_markers.clinical_label",
                    "count": {"$sum": 1},
                    "avg_intensity": {"$avg": "$clinical_markers.intensity"}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 5
            }
        ]
        
        top_conditions = await db.sessions.aggregate(pipeline_conditions).to_list(None)
        
        return {
            "user_id": user_id,
            "period": "last_30_days",
            "top_emotions": top_emotions,
            "top_conditions": top_conditions,
            "total_sessions": len(await db.sessions.find({"user_id": user_id}).to_list(None))
        }
        
    except Exception as e:
        print(f"Insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


# ============================================================================
# STEP 4: Optional - Add a crisis detection endpoint
# ============================================================================

@app.get("/crisis-check/{user_id}")
async def check_for_crisis_indicators(user_id: str):
    """
    Checks for high-risk patterns in the last 24 hours.
    """
    try:
        last_24h = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        
        high_risk_sessions = await db.sessions.find({
            "user_id": user_id,
            "timestamp": {"$gte": last_24h},
            "clinical_markers.intensity": {"$gte": 9}
        }).to_list(None)
        
        crisis_conditions = [
            "PTSD", "C-PTSD", "Suicidal", "Crisis", "Emergency"
        ]
        
        crisis_markers = await db.sessions.find({
            "user_id": user_id,
            "timestamp": {"$gte": last_24h},
            "clinical_markers.clinical_label": {
                "$in": crisis_conditions
            }
        }).to_list(None)
        
        return {
            "user_id": user_id,
            "high_intensity_sessions": len(high_risk_sessions),
            "crisis_indicators_found": len(crisis_markers) > 0,
            "recommended_action": "Contact mental health professional" if len(crisis_markers) > 0 else "Continue monitoring"
        }
        
    except Exception as e:
        print(f"Crisis check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check crisis indicators")


# ============================================================================
# TESTING: Example payloads
# ============================================================================

"""
Test the system with these example requests:

1. Basic message:
   POST /chat?user_id=test_user&message=I%20feel%20paralyzed%20by%20perfectionism

2. Check insights:
   GET /insights/test_user

3. Check for crisis:
   GET /crisis-check/test_user

Expected MongoDB document after processing:
{
  "_id": ObjectId(...),
  "user_id": "test_user",
  "timestamp": ISODate("2026-04-03T..."),
  "message": "I feel paralyzed by perfectionism",
  "ai_reply": "It sounds like you're setting really high standards...",
  "clinical_markers": {
    "emotion_tag": "Paralyzed",
    "emotion_cluster": "COMPLEX",
    "clinical_label": "Perfectionism (Maladaptive)",
    "clinical_category": "IDENTITY_PERSONALITY",
    "intensity": 8,
    "trigger_source": "Performance",
    "is_recurring": true,
    "functional_impact": 7,
    "reasoning": "Perfectionist paralysis with high performance anxiety"
  }
}
"""
