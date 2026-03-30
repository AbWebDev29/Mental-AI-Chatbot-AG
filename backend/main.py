import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Internal module imports
from database import connect_to_mongo, save_session_data, db
from nlp_engine import get_clinical_markers
# 1. Environment Configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

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

# Initialize Gemini Client for 2026 Stable SDK
client_ai = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options=types.HttpOptions(api_version='v1')
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
    Processes user message with 'Clinical Memory'.
    Uses the 3-9 Scale and History to provide targeted mental health support.
    """
    # 1. Run NLP Audit on the current message
    markers = await get_clinical_markers(message)
    ai_reply = ""
    
    try:
        # 2. FETCH CLINICAL HISTORY (The Memory)
        # We grab the last 3 entries to see the trend in Thinking/Doing
        history_cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(3)
        past_sessions = await history_cursor.to_list(length=3)
        
        # Format history for the AI prompt
        history_context = ""
        if past_sessions:
            history_context = "PAST CLINICAL CONTEXT:\n"
            for s in reversed(past_sessions):
                m = s.get('clinical_markers', {})
                history_context += f"- User said: '{s['message']}' | State: {m.get('state')} | Mind Intensity: {m.get('thinking_intensity')}/9\n"

        # 3. CONSTRUCT THE MASTER PROMPT
        # This uses your 3-9 Scale Theory and Biome concepts
        system_instruction = f"""
        ROLE: You are an empathetic Clinical AI Sidekick (Persona: Cherub/Angel).
        THEORY: You monitor mental health using a 3-9 intensity scale (Thinking vs Doing).
        
        {history_context}
        
        CURRENT STATE:
        - Biome: {markers['state']}
        - Thinking Intensity (Mind): {markers['thinking_intensity']}/9
        - Doing Intensity (Might): {markers['doing_intensity']}/9
        
        USER MESSAGE: "{message}"
        
        TASK:
        1. Acknowledge the user's feelings with deep empathy.
        2. If Thinking (Mind) is >= 7, guide them with a 'Grounding Game' (like identifying objects in the room).
        3. If Intensity is low (3-4), offer a 'Micro-Spark' of motivation.
        4. Refer to the 'Past Context' if it shows a pattern (e.g., 'I noticed you've been feeling lonely in our last few chats').
        """

        # 4. CALL GEMINI
        response = client_ai.models.generate_content(
            model="gemini-2.0-flash", 
            contents=system_instruction
        )
        ai_reply = response.text if response.text else "I am holding space for you. Tell me more."

    except Exception as e:
        # handle quota and other errors gracefully with i18n-friendly fallback
        print(f"⚠️ AI ERROR: {str(e)}")
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e).upper():
            ai_reply = (
                "I'm currently on fallback mode due to API quota limits,"
                " but I'm still here to listen: "
                "".join(["\n", "- Remember that your experience is valid.", "\n", "- You can reflect more deeply on what you shared."])
            )
        else:
            ai_reply = "I'm here, but I'm having a little trouble connecting to my thoughts. I've noted your feelings."

    # 5. SAVE TO MONGODB (Ensures clinical persistence)
    session_entry = {
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "message": message,
        "ai_reply": ai_reply,
        "clinical_markers": markers
    }
    await save_session_data(user_id, session_entry)
    
    return {"reply": ai_reply, "analysis": markers}

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
    Retrieves the chronological journey of the user.
    """
    try:
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", 1)
        history = await cursor.to_list(length=100)
        
        if not history:
            return {"user_id": user_id, "count": 0, "history": []}

        for entry in history:
            entry["_id"] = str(entry["_id"])
            
        return {"user_id": user_id, "count": len(history), "history": history}
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Database retrieval failed")