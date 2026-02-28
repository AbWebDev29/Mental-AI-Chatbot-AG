import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Body, HTTPException
from google import genai
from google.genai import types

# Internal module imports
from .database import connect_to_mongo, save_session_data, db
from .nlp_engine import get_clinical_markers

# 1. Environment Configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# 2. Initialization
app = FastAPI(title="Clinical AI Assistant API")

# Initialize Gemini Client for 2026 Stable SDK
# Using http_options to force the production v1 endpoint
client_ai = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options=types.HttpOptions(api_version='v1')
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

# --- ROUTES ---

@app.post("/chat")
async def chat_with_analysis(user_id: str, message: str):
    try:
        # 1. Run NLP Audit (spaCy-based marker detection)
        markers = get_clinical_markers(message)
        
        # 2. Prepare Clinical Prompt with your 3-9 Scale Theory
        prompt = f"""
        Role: Specialized Mental Health Assistant.
        Theory: Analyze user intensity on a scale of 3-9.
        Detected Markers: {markers['state']} (Thinking: {markers['thinking_intensity']}, Doing: {markers['doing_intensity']}).
        
        User Message: "{message}"
        
        Task: Provide an empathetic response based on the intensity.
        If intensity is high (7-9), prioritize grounding techniques. 
        If intensity is low (3-5), focus on reflection.
        """
        
        # 3. Call current 2026 Stable Model (Gemini 2.0 Flash)
        # Note: If you want the absolute latest, use "gemini-3-flash"
        response = client_ai.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        ai_reply = response.text if response.text else "I'm here to listen. Can you tell me more about what's on your mind?"

        # 4. Save structured data to MongoDB
        session_entry = {
            "user_id": user_id,
            "timestamp": datetime.datetime.utcnow(),
            "message": message,
            "ai_reply": ai_reply,
            "clinical_markers": markers
        }
        
        await save_session_data(user_id, session_entry)
        
        return {
            "reply": ai_reply, 
            "analysis": markers
        }

    except Exception as e:
        error_msg = str(e)
        # Graceful handling for Rate Limits (429)
        if "429" in error_msg:
            return {
                "reply": "I'm reflecting on your thoughts. Please give me a moment to process.",
                "analysis": {"state": "Rate Limited", "thinking_intensity": 0, "doing_intensity": 0}
            }
        
        print(f"❌ CHAT ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
@app.get("/history/{user_id}")
async def get_patient_history(user_id: str):
    """
    Retrieves chronological chat history for a specific user.
    """
    try:
        # 1. Query 'sessions' collection (sorting by timestamp)
        cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", 1)
        
        # 2. Convert cursor to list (limit to last 100 for performance)
        history = await cursor.to_list(length=100)
        
        if not history:
            raise HTTPException(status_code=404, detail="No history found for this user")

        # 3. Format data for JSON response
        for entry in history:
            entry["_id"] = str(entry["_id"])
            
        return {
            "user_id": user_id,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))