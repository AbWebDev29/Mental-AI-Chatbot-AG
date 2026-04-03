import os
import datetime
import certifi  # <--- Step 1: Import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Step 2: Get the path to the certificate bundle
ca = certifi.where()

# Step 3: Initialize the client with the tlsCAFile parameter
mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")

# We pass the 'ca' path here so Python trusts the MongoDB certificate
client = AsyncIOMotorClient(mongo_uri, tlsCAFile=ca)
db = client.get_database("mental_health_db")

async def connect_to_mongo():
    try:
        # A ping verifies the "handshake" is successful
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas with SSL Fix")
    except Exception as e:
        print(f"❌ Could not connect to MongoDB: {e}")

async def save_session_data(user_id: str, message: str, ai_reply: str, markers: dict):
    collection = db.sessions
    print(f"Attempting to save session for user {user_id}")
    try:
        await collection.insert_one(
            {
                "user_id": user_id,
                "timestamp": datetime.datetime.utcnow(),
                "message": message,
                "ai_reply": ai_reply,
                "clinical_markers": markers,
            }
        )
        print("✅ Session saved successfully")
    except Exception as e:
        print(f"❌ MongoDB write failed for user {user_id}: {e}")
        raise