import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from google import genai

# Correct internal imports
from .database import connect_to_mongo, save_session_data
from .nlp_engine import get_clinical_markers

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# LETS PRINT ALL KEYS LOADED (Security note: only for debugging!)
print(f"--- DEBUGGING ENV LOAD ---")
print(f"Path: {env_path}")
print(f"File exists? {env_path.exists()}")
print(f"Key in environment: {os.environ.get('GOOGLE_API_KEY') is not None}")
print(f"--------------------------")


from fastapi import FastAPI
from google import genai
from .database import connect_to_mongo, save_session_data

app = FastAPI()

# 2. NOW INITIALIZE THE CLIENT
# It will now correctly find the key in your .env
client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.post("/chat")
async def chat(user_id: str, message: str):
    response = client_ai.models.generate_content(
        model="gemini-2.0-flash", 
        contents=message
    )
    
    await save_session_data(user_id, {
        "user_message": message,
        "bot_response": response.text
    })
    
    return {"response": response.text}

from .nlp_engine import get_clinical_markers
from .database import save_session_data
import datetime

@app.post("/chat")
async def chat_with_analysis(user_id: str, message: str):
    # STEP 1: Run spaCy Audit
    markers = get_clinical_markers(message)
    
    # STEP 2: Prompt Gemini with Clinical Guidelines
    clinical_prompt = f"""
    You are a specialized mental health assistant.
    The user's detected state is: {markers['state']}.
    User message: "{message}"
    
    Apply the 3-9 intensity scale. 
    1. Provide an empathetic response.
    2. At the end of your response, add a hidden tag: [SCORE: X] where X is 3-9.
    """
    
    response = client_ai.models.generate_content(
        model="gemini-2.0-flash", 
        contents=clinical_prompt
    )
    
    # STEP 3: Store structured data in MongoDB
    session_entry = {
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "message": message,
        "ai_reply": response.text,
        "clinical_markers": markers,
        "is_processed": True
    }
    
    await save_session_data(user_id, session_entry)
    
    return {
        "reply": response.text,
        "analysis": markers
    }


from fastapi import HTTPException
from .database import db # Ensure your database.py exports 'db'

@app.get("/history/{user_id}")
async def get_patient_history(user_id: str):
    # 1. Look into the 'sessions' collection in MongoDB
    cursor = db.sessions.find({"user_id": user_id}).sort("timestamp", 1)
    
    # 2. Convert the database results into a list
    history = await cursor.to_list(length=100)
    
    if not history:
        raise HTTPException(status_code=404, detail="No history found for this user")

    # 3. Clean up the data for the frontend (removing MongoDB internal IDs)
    for entry in history:
        entry["_id"] = str(entry["_id"])
        
    return {
        "user_id": user_id,
        "count": len(history),
        "history": history
    }