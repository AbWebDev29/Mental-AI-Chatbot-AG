

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