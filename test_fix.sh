#!/bin/bash
# Fix and restart backend

cd /Users/anvibansal/mental-app

# Activate venv
source venv/bin/activate

# Navigate to backend
cd backend

# Kill existing server
pkill -f "uvicorn main:app" || true

# Wait a moment
sleep 1

# Start server with reload
uvicorn main:app --reload &

# Wait for startup
sleep 3

# Make test request
echo "Making test request..."
curl -s "http://localhost:8000/chat?user_id=test_user&message=I%20feel%20so%20disconnected%20and%20alone" > /tmp/test_response.json

# Display response
echo "Response received. Checking clinical_markers..."
cat /tmp/test_response.json | python3 -m json.tool 2>/dev/null | grep -A 15 "clinical_markers" || echo "Raw response:" && cat /tmp/test_response.json

echo ""
echo "✅ Test complete. Check MongoDB for full document."
