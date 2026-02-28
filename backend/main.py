import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

# Internal module imports (Ensure these files exist in your directory)
from .database import connect_to_mongo, save_session_data, db
from .nlp_engine import get_clinical_markers

# 1. Environment Configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# 2. Initialization
app = FastAPI(title="Clinical AI Assistant API")

# --- CORS MIDDLEWARE ---
# This allows your Next.js frontend (port 3000) to access this API (port 8000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client for 2026 Stable SDK
# We force 'v1' to avoid the 404 errors common with 'v1beta'
client_ai = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options=types.HttpOptions(api_version='v1')
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

# --- ROUTES ---

@app.post("/chat")
async def chat_with_analysis(user_id: str = Query(...), message: str = Query(...)):
    # 1. ALWAYS run the NLP Audit first
    markers = get_clinical_markers(message)
    ai_reply = ""
    
    try:
        # 2. Prepare the prompt
        prompt = f"Mental Health Assistant context: {markers['state']}. User says: {message}"
        
        # 3. Attempt to call Gemini
        response = client_ai.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        ai_reply = response.text if response.text else "I'm here to listen."

    except Exception as e:
        if "429" in str(e):
            ai_reply = "I'm reflecting on your thoughts. (Note: Clinical markers were saved)."
        else:
            ai_reply = "I'm having trouble connecting, but I've noted your feelings."

    # 4. CRITICAL: Save to MongoDB OUTSIDE the try/except block
    # This ensures history is updated even if Gemini fails
    session_entry = {
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "message": message,
        "ai_reply": ai_reply,
        "clinical_markers": markers
    }
    await save_session_data(user_id, session_entry)
    
    return {"reply": ai_reply, "analysis": markers}
@app.get("/history/{user_id}")
async def get_patient_history(user_id: str):
    try:
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", 1)
        history = await cursor.to_list(length=100)
        
        # If no history, just return an empty list instead of crashing
        if not history:
            return {"user_id": user_id, "count": 0, "history": []}

        for entry in history:
            entry["_id"] = str(entry["_id"])
            
        return {"user_id": user_id, "count": len(history), "history": history}
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Database retrieval failed")