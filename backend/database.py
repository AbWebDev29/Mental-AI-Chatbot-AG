import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# We define the client at the top level so other files can import it
client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.get_database("mental_health_db")

async def connect_to_mongo():
    # Just a ping to verify connection
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Could not connect to MongoDB: {e}")

async def save_session_data(user_id: str, data: dict):
    collection = db.sessions
    await collection.insert_one({"user_id": user_id, **data})