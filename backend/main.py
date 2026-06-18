import os
import datetime
import difflib
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Union

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import certifi
from motor.motor_asyncio import AsyncIOMotorClient # or MongoClient if you use the sync version

# 1. Environment Configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Internal module imports
from database import connect_to_mongo, save_session_data, db
from nlp_engine import get_clinical_markers, get_secondary_variation, get_opening_phrase, get_llama_clinical_analysis
from llm_service import generate_llama_response

# 2. Initialization
app = FastAPI(title="Clinical AI Assistant API")

# --- CORS MIDDLEWARE ---
origins = ["*"]  # Allow all origins during local dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("startup")
async def create_test_user():
    # This will create a user automatically so you can test Sign In
    user = await db.users.find_one({"email": "test@me.com"})
    if not user:
        await db.users.insert_one({"email": "test@me.com", "password": "123", "full_name": "Test User"})
        print("👤 Test user created: test@me.com / 123")

# --- ROUTES ---

@app.post("/chat")
async def chat_with_analysis(user_id: str = Query(...), message: str = Query(...), session_id: str = Query(default="default")):
    """
    Processes user message with 'Adaptive Intent Detection' and 'Loop Prevention'.
    """
    # 1. Fetch Chat History
    cursor = db.sessions.find({"user_id": user_id, "session_id": session_id}).sort("timestamp", -1).limit(10)
    history_docs: List[Dict[str, Any]] = await cursor.to_list(length=5)
    
    # Extract Last AI message for 'Question-Answer Detection'
    last_ai_msg = history_docs[0].get("ai_reply", "") if history_docs else ""
    # Use a loop to avoid slice-related lint issues in certain environments
    last_responses = []
    for doc in history_docs:
        if len(last_responses) >= 2: break
        last_responses.append(str(doc.get("ai_reply", "")))
    
    # 2. Clean History for Context Layer
    history_docs = list(reversed(history_docs))
    clean_history = [
        {"user": doc.get("message", ""), "ai": doc.get("ai_reply", ""), "markers": doc.get("markers", {})}
        for doc in history_docs
    ]
    
    # 3. Create Context Layer from History
    context_from_history = "\n".join([f"User: {h['user']} AI: {h['ai']}" for h in clean_history])
    
    # 4. Call Llama 3.2 instead of old markers logic
    try:
        ai_reply = generate_llama_response(message, context_from_history)
    except Exception as e:
        print(f"Llama Error: {e}")
        ai_reply = "I'm here, but I'm having a little trouble thinking. Can we try that again?"

    # 5. Get Clinical Analysis from Llama Taxonomy System
    clinical_analysis = {}
    try:
        # Pass clean_history as-is (it has the right format)
        clinical_analysis = get_llama_clinical_analysis(message, clean_history)
    except Exception as e:
        print(f"⚠️ Clinical Analysis Error: {e}")
        # Fallback: use safe defaults
        clinical_analysis = {
            "emotion_tag": "Overwhelmed",
            "emotion_cluster": "COMPLEX",
            "clinical_label": "Emotional Distress",
            "clinical_category": "MOOD",
            "intensity": 5,
            "trigger_source": "Unknown",
            "is_recurring": False,
            "functional_impact": 5,
            "reasoning": "Analysis unavailable"
        }

    # 6. Create basic markers for the database (UPDATED to include clinical analysis)
    markers = {
        "status": "Conversing",
        "model": "llama-3.2-3b"
    }

    # 6. ANTI-IDENTICAL & LOOP PREVENTION (Gentle)
    is_repeat = False
    hard_pivot_msg = ""
    
    # Check last 2 AI replies for semantic match
    for i, prev_reply in enumerate(last_responses):
        ratio = difflib.SequenceMatcher(None, ai_reply.lower(), prev_reply.lower()).ratio()
        
        if ai_reply.strip() == prev_reply.strip():
            print(f"🚨 EXACT MATCH DETECTED: Forcing Breathing Pivot")
            hard_pivot_msg = "I want to make sure I'm truly listening. Let's set the usual talk aside—how are you actually breathing right now? Is it shallow or deep?"
            is_repeat = True
            break
        elif ratio > 0.95:  # Only pivot if almost identical
            print(f"⚠️ SEMANTIC MATCH (>95%): Forcing Sleep Pivot")
            hard_pivot_msg = "I want to make sure I'm not just repeating myself while you're going through this. Let's look at one specific thing: How is your sleep holding up through all this stress?"
            is_repeat = True
            break
            
    if is_repeat:
        ai_reply = hard_pivot_msg
        markers["source"] = "absolute_repetition_guard"

    # 7. Save and Return
    await save_session_data(user_id, message, ai_reply, clinical_analysis, session_id)
    return {"reply": ai_reply, "analysis": clinical_analysis, "markers": markers}

# --- AUTH ROUTES ---
class UserAuth(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

@app.post("/auth/signup")
async def signup(auth: UserAuth):
    existing = await db.users.find_one({"email": auth.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = await db.users.insert_one({
        "email": auth.email,
        "auth_provider": "email",
        "password": auth.password,  # Note: In production, use hashing (bcrypt)
        "full_name": auth.full_name,
        "created_at": datetime.datetime.utcnow()
    })
    return {"user_id": str(new_user.inserted_id), "status": "success"}

@app.post("/auth/signin")
async def signin(auth: UserAuth):
    user = await db.users.find_one({"email": auth.email,
        "auth_provider": "email", "password": auth.password})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "user_id": str(user["_id"]),
        "full_name": user.get("full_name"),
        "status": "success"
    }

@app.get("/history/{user_id}")
async def get_patient_history(user_id: str):
    """
    Returns the latest 5 sessions for this user.
    """
    try:
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(20)
        history = await cursor.to_list(length=5)

        for entry in history:
            entry["_id"] = str(entry["_id"])

        return history
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Database retrieval failed")
    
from llm_service import generate_llama_response

@app.delete("/auth/delete/{user_id}")
async def delete_account(user_id: str):
    from bson import ObjectId
    try:
        # Delete user
        await db.users.delete_one({"_id": ObjectId(user_id)})
        # Delete all their chat sessions too
        await db.sessions.delete_many({"user_id": user_id})
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SESSION ROUTES ---

@app.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Returns grouped conversations for the sidebar.
    Each session has a session_id, first message, and timestamp.
    """
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$session_id",
                "first_message": {"$last": "$message"},
                "last_time": {"$first": "$timestamp"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"last_time": -1}},
            {"$limit": 20}
        ]
        sessions = await db.sessions.aggregate(pipeline).to_list(length=20)
        for s in sessions:
            s["session_id"] = str(s["_id"])
            del s["_id"]
            s["last_time"] = str(s["last_time"])
        return sessions
    except Exception as e:
        print(f"❌ SESSIONS ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session_messages(session_id: str):
    """
    Returns all messages for a specific session.
    """
    try:
        cursor = db.sessions.find({"session_id": session_id}).sort("timestamp", 1)
        messages = await cursor.to_list(length=100)
        for m in messages:
            m["_id"] = str(m["_id"])
            m["timestamp"] = str(m["timestamp"])
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{user_id}")
async def get_user_memory(user_id: str):
    """
    Returns a memory summary of the user's past conversations.
    Used to give the bot context about who the user is.
    """
    try:
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(50)
        history = await cursor.to_list(length=50)

        emotions = [h.get("clinical_markers", {}).get("emotion_tag") for h in history if h.get("clinical_markers")]
        emotions = [e for e in emotions if e]

        topics = [h.get("message", "")[:60] for h in history[:5]]

        top_emotion = None
        if emotions:
            freq = {}
            for e in emotions:
                freq[e] = freq.get(e, 0) + 1
            top_emotion = max(freq, key=freq.get)

        return {
            "total_sessions": len(history),
            "top_emotion": top_emotion,
            "recent_topics": topics,
            "last_session": str(history[0]["timestamp"]) if history else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SECURE GOOGLE AUTH ---
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = "482645097952-9ltr5vpaoh9e0totmj00qj19f5u87ltp.apps.googleusercontent.com"

class GoogleAuthRequest(BaseModel):
    token: str

@app.post("/auth/google")
async def google_auth(body: GoogleAuthRequest):
    try:
        # Verify the token with Google's servers
        idinfo = id_token.verify_oauth2_token(
            body.token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name", email.split("@")[0])
        google_id = idinfo.get("sub")  # unique Google user ID
        picture = idinfo.get("picture", "")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        # Check if user exists
        user = await db.users.find_one({"email": email})

        if user:
            # If user exists but was created with password (not Google), block them
            if user.get("auth_provider") == "email":
                raise HTTPException(
                    status_code=400,
                    detail="This email is registered with a password. Please sign in with email instead."
                )
            # Update their info in case name/picture changed
            await db.users.update_one(
                {"email": email},
                {"$set": {"full_name": name, "picture": picture, "google_id": google_id}}
            )
        else:
            # Create new Google user
            await db.users.insert_one({
                "email": email,
                "full_name": name,
                "google_id": google_id,
                "picture": picture,
                "auth_provider": "google",
                "created_at": datetime.datetime.utcnow()
            })
            user = await db.users.find_one({"email": email})

        return {
            "user_id": str(user["_id"]),
            "full_name": name,
            "email": email,
            "picture": picture,
            "status": "success"
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
