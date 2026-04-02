import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# We define the client at the top level so other files can import it
mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
client = AsyncIOMotorClient(mongo_uri)
db = client.get_database("mental_health_db")

async def connect_to_mongo():
    # Just a ping to verify connection
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas")
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