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

async def save_session_data(user_id: str, message: str, ai_reply: str, markers: dict, session_id: str = "default"):
    collection = db.sessions
    print(f"Attempting to save session for user {user_id}")
    try:
        await collection.insert_one(
            {
                "user_id": user_id,
                "session_id": session_id,
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


async def get_latest_session_messages(user_id: str, max_messages: int = 200):
    """
    Return the chronological messages for the single most-recent session for `user_id`.

    Steps:
    1) Find the absolute newest document for the user, sorting by `timestamp` DESC.
       Falls back to sorting by `_id` DESC if `timestamp` is missing.
    2) Use that document's `session_id` to fetch all records for that session,
       sorted by `timestamp` ASC (chronological). If `timestamp` is missing on
       documents, sorting by `_id` ASC provides approximate chronological order.
    3) Returns a list of dicts containing `timestamp`, `message`, and `ai_reply`.
    """
    coll = db.sessions

    # Attempt to get newest by timestamp first
    latest = await coll.find({"user_id": user_id}).sort("timestamp", -1).limit(1).to_list(length=1)
    if not latest:
        # Fallback to _id (ObjectId creation time)
        latest = await coll.find({"user_id": user_id}).sort("_id", -1).limit(1).to_list(length=1)

    if not latest:
        return []

    latest_doc = latest[0]
    session_id = latest_doc.get("session_id")

    # Build thread query — restrict to that session if available
    query = {"user_id": user_id}
    if session_id is not None:
        query["session_id"] = session_id

    # Fetch full thread in chronological order
    # Prefer timestamp ascending; if timestamps missing, Mongo will still return documents
    thread_docs = await coll.find(query).sort("timestamp", 1).to_list(length=max_messages)

    # Normalize output
    out = []
    for d in thread_docs:
        out.append({
            "timestamp": d.get("timestamp") or d.get("_id"),
            "message": d.get("message", ""),
            "ai_reply": d.get("ai_reply", ""),
        })

    return out