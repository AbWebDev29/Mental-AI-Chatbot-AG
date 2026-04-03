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
from nlp_engine import get_clinical_markers, get_secondary_variation, get_opening_phrase

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
async def chat_with_analysis(user_id: str = Query(...), message: str = Query(...)):
    """
    Processes user message with 'Adaptive Intent Detection' and 'Loop Prevention'.
    """
    # 1. Fetch Chat History
    cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
    history_docs: List[Dict[str, Any]] = await cursor.to_list(length=5)
    
    # Extract Last AI message for 'Question-Answer Detection'
    last_ai_msg = history_docs[0].get("ai_reply", "") if history_docs else ""
    # Use a loop to avoid slice-related lint issues in certain environments
    last_responses = []
    for doc in history_docs:
        if len(last_responses) >= 2: break
        last_responses.append(str(doc.get("ai_reply", "")))
    
    # 2. Sequential Logic: Did the user answer a relief question?
    relief_keywords = ["show", "game", "movie", "distraction", "relief", "quit"]
    user_answered_relief = any(kw in message.lower() for kw in relief_keywords)
    ai_asked_relief = "?" in last_ai_msg and ("relief" in last_ai_msg.lower() or "look like" in last_ai_msg.lower())
    
    # 3. Clean History for Reasoning
    history_docs = list(reversed(history_docs))
    clean_history = [
        {"user": doc.get("message", ""), "ai": doc.get("ai_reply", ""), "markers": doc.get("markers", {})}
        for doc in history_docs
    ]
    
    # Reset context if major shift, but preserve crisis memory
    recent_is_crisis = any("dissociation" in str(doc.get("markers", {}).get("mental_health_pattern", "")).lower() for doc in history_docs)
    
    reset_context = False
    IDENTITY_KEYWORDS = {"mirror", "myself", "identity", "tricking", "bad person"}
    if any(kw in message.lower() for kw in IDENTITY_KEYWORDS) and not recent_is_crisis:
        # Topic shift detect logic can be expanded here
        pass

    # 4. Primary Reasoning (Adaptive)
    markers = await get_clinical_markers(message, history=clean_history, reset_context=reset_context)
    ai_reply = str(markers.get("ai_reply", "I'm listening.")).strip()

    # 5. ANTI-IDENTICAL & LOOP PREVENTION
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
        elif ratio > 0.7:
            print(f"⚠️ SEMANTIC MATCH (>70%): Forcing Sleep Pivot")
            hard_pivot_msg = "I want to make sure I'm not just repeating myself while you're going through this. Let's look at one specific thing: How is your sleep holding up through all this stress?"
            is_repeat = True
            break
            
    if is_repeat:
        ai_reply = hard_pivot_msg
        markers["ai_reply"] = ai_reply
        markers["source"] = "absolute_repetition_guard"

    # 6. Save and Return
    await save_session_data(user_id, message, ai_reply, markers)
    return {"reply": ai_reply, "analysis": markers, "markers": markers}

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
        "password": auth.password,  # Note: In production, use hashing (bcrypt)
        "full_name": auth.full_name,
        "created_at": datetime.datetime.utcnow()
    })
    return {"user_id": str(new_user.inserted_id), "status": "success"}

@app.post("/auth/signin")
async def signin(auth: UserAuth):
    user = await db.users.find_one({"email": auth.email, "password": auth.password})
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
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
        history = await cursor.to_list(length=5)

        for entry in history:
            entry["_id"] = str(entry["_id"])

        return history
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Database retrieval failed")
    