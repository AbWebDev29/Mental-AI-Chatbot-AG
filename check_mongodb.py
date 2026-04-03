#!/usr/bin/env python3
import asyncio
from backend.database import db
from datetime import datetime, timedelta

async def check_sessions():
    collection = db.sessions
    now = datetime.utcnow()
    
    # Find test sessions from the last 5 minutes
    sessions = await collection.find({
        'user_id': {'$in': ['test_user_debug', 'test_user_debug2']},
        'timestamp': {'$gte': now - timedelta(minutes=5)}
    }).sort('timestamp', -1).to_list(length=None)
    
    print(f"\nFound {len(sessions)} recent test sessions\n")
    
    for i, session in enumerate(sessions):
        print(f"Session {i+1}:")
        print(f"  User: {session['user_id']}")
        print(f"  Message: {session['message'][:50]}...")
        markers = session.get('clinical_markers', {})
        print(f"  Clinical Markers:")
        print(f"    - emotion_tag: {markers.get('emotion_tag')}")
        print(f"    - emotion_cluster: {markers.get('emotion_cluster')}")
        print(f"    - clinical_label: {markers.get('clinical_label')}")
        print(f"    - clinical_category: {markers.get('clinical_category')}")
        print(f"    - trigger_source: {markers.get('trigger_source')}")
        print()

asyncio.run(check_sessions())
