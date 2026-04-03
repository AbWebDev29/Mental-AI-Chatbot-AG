# 🔧 TROUBLESHOOTING GUIDE: "System Error" in Clinical Markers

## Problem: Both messages show `"System error - using default classification"`

Your `clinical_markers` are defaulting to:
```json
{
  "emotion_tag": "Overwhelmed",
  "clinical_label": "GAD",
  "intensity": 5,
  "reasoning": "System error - using default classification"
}
```

This means the `get_clinical_taxonomy_analysis()` function is hitting the **fallback error handler** instead of successfully calling Ollama.

---

## Root Causes & Solutions

### 1. ❌ Ollama Not Running

**Symptom:** Error message in backend logs like `Connection refused` or `Ollama not found`

**Solution:**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Verify the model is available
ollama list

# Should show: llama3.2:3b    6.5 GB    ...

# If not installed, download it:
ollama pull llama3.2:3b
```

---

### 2. ❌ JSON Mode Not Supported

**Symptom:** `"reasoning": "System error - using default classification"` but no explicit error in logs

**Solution:** 
Make sure you're using Ollama's JSON mode correctly:

```python
# CORRECT:
response = ollama.chat(
    model="llama3.2:3b",
    format="json",  # ✅ This forces JSON output
    messages=[...]
)

# WRONG (will cause failures):
response = ollama.chat(
    model="llama3.2:3b",
    # ❌ Missing format="json"
    messages=[...]
)
```

**Verify JSON mode works:**
```bash
# Run the diagnostic
cd /Users/anvibansal/mental-app/backend
python diagnose_ollama.py
```

---

### 3. ❌ System Prompt Too Long

**Symptom:** Ollama times out or returns garbage

**Solution:** The current system prompt is ~1500 tokens. If Ollama is struggling:

```python
# In clinical_analyzer_llama.py, simplify the prompt:

system_prompt = """
You are a clinical NLP system. Respond ONLY with JSON.

EMOTIONS (Pick ONE): 
Ecstatic, Elated, Serene, Dejected, Anguished, Forlorn, Infuriated, Resentful, 
Bitter, Petrified, Apprehensive, Frazzled, Overwhelmed, Mortified, Inadequate, 
Alienated, Disconnected

CONDITIONS (Pick ONE):
GAD, MDD, PTSD, Panic Disorder, Social Anxiety, BPD, OCD, Insomnia, Dysthymia

Return JSON with: emotion, clinical_condition, intensity (1-10), reasoning
"""
```

---

### 4. ❌ Ollama Memory Issue

**Symptom:** Works for first request, then fails

**Solution:** Ollama runs out of VRAM on MacBook Air with 8GB

```bash
# Check available VRAM
top -l1 | grep "Phys"

# If memory is constrained, use a smaller model:
ollama pull llama2:7b  # Smaller than 3.2:3b

# Update clinical_analyzer_llama.py:
response = ollama.chat(
    model="llama2:7b",  # Use smaller model
    format="json",
    messages=[...]
)
```

---

### 5. ❌ JSON Parsing Error

**Symptom:** Ollama returns valid JSON but parser fails

**Solution:** The response cleanup might be stripping valid JSON

```python
# In clinical_analyzer_llama.py, add debug logging:

response_text = response["message"]["content"].strip()

# ADD THIS DEBUG LINE:
print(f"🔍 Raw Ollama response:\n{response_text}\n")

# Then try to parse:
try:
    analysis = json.loads(response_text)
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing failed: {e}")
    print(f"Response was: {response_text[:200]}")
    return get_fallback_analysis(user_input)
```

---

## Diagnostic Steps (In Order)

### Step 1: Verify Ollama Connection
```bash
cd /Users/anvibansal/mental-app/backend
python diagnose_ollama.py
```

**Expected output:**
```
✅ Ollama is running
✅ JSON Mode Test Response: {"test": "works"}
✅ Response is valid JSON
✅ Successfully parsed as JSON
✅ ALL DIAGNOSTIC TESTS PASSED
```

---

### Step 2: Check System Logs
```bash
# Check backend logs for errors
cd /Users/anvibansal/mental-app/backend
uvicorn main:app --reload --log-level DEBUG

# Make a test request and watch for errors:
curl "http://localhost:8000/chat?user_id=test&message=I%20feel%20sad"
```

**Look for:**
- ✅ `"emotion": "Dejected"` (not "Overwhelmed")
- ❌ `"System error - using default classification"`

---

### Step 3: Test Directly
```bash
# Create a test file
cat > /Users/anvibansal/mental-app/backend/test_direct.py << 'EOF'
from clinical_analyzer_llama import get_clinical_taxonomy_analysis
import json

msg = "I'm surrounded by people but I've never felt more alone"
result = get_clinical_taxonomy_analysis(msg)
print(json.dumps(result, indent=2))
EOF

# Run it
python test_direct.py
```

**Expected:**
```json
{
  "emotion": "Alienated",
  "clinical_condition": "Social Anxiety",
  "intensity": 8,
  ...
}
```

---

### Step 4: Check MongoDB
```bash
# Open MongoDB Compass
# Navigate to: mental_health_db > sessions
# Look at latest document's "clinical_markers" field

# Should look like:
{
  "emotion_tag": "Alienated",      ✅ (NOT "Overwhelmed")
  "clinical_label": "Social Anxiety", ✅ (NOT "GAD")
  "intensity": 8,
  "reasoning": "User feels isolated..."
}
```

---

## Quick Fixes (Try These First)

### Fix 1: Restart Everything
```bash
# Kill any running services
pkill -f "ollama serve"
pkill -f "uvicorn"

# Restart Ollama
ollama serve &

# Wait 5 seconds, then restart backend
cd /Users/anvibansal/mental-app/backend
uvicorn main:app --reload
```

### Fix 2: Clear Ollama Cache
```bash
# Stop Ollama
ollama serve shutdown

# Remove model
rm -rf ~/.ollama/models/blobs/llama3.2:3b

# Re-download
ollama pull llama3.2:3b
```

### Fix 3: Simplify the Prompt
Edit `clinical_analyzer_llama.py` line 50-60 and reduce the taxonomy list to top 20 emotions/conditions.

### Fix 4: Enable Debug Logging
Add this to the top of `clinical_analyzer_llama.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Then in get_clinical_taxonomy_analysis():
logger.debug(f"Sending prompt to Ollama...")
logger.debug(f"Response: {response_text}")
```

---

## If Still Not Working

Run this comprehensive test:

```bash
cd /Users/anvibansal/mental-app/backend
python diagnose_ollama.py 2>&1 | tee diagnostic_output.txt

# Then check the output file
cat diagnostic_output.txt
```

**Share the output** and I can help debug further.

---

## Expected Behavior (When Fixed)

**Before (❌ BROKEN):**
```json
{
  "emotion_tag": "Overwhelmed",
  "clinical_label": "GAD",
  "intensity": 5,
  "reasoning": "System error - using default classification"
}
```

**After (✅ WORKING):**
```json
{
  "emotion_tag": "Alienated",
  "emotion_cluster": "COMPLEX",
  "clinical_label": "Social Anxiety Disorder",
  "clinical_category": "ANXIETY",
  "intensity": 8,
  "trigger_source": "Social Disconnection",
  "is_recurring": true,
  "functional_impact": 7,
  "reasoning": "User experiences profound disconnection despite social presence"
}
```

---

## Next Steps

1. ✅ Run `python diagnose_ollama.py`
2. ✅ Check Ollama is running: `ollama list`
3. ✅ Verify JSON mode works
4. ✅ Restart backend server
5. ✅ Make test request and verify MongoDB
6. ✅ Check for proper classification (not "Overwhelmed/GAD" defaults)

---

## MongoDB Query to Check Status

```javascript
// Check all messages from last hour
db.sessions.find({
  timestamp: {$gte: new Date(new Date() - 60*60*1000)}
})
.pretty()

// Count how many are still using fallback
db.sessions.aggregate([
  {$match: {timestamp: {$gte: new Date(new Date() - 24*60*60*1000)}}},
  {$group: {
    _id: "$clinical_markers.reasoning",
    count: {$sum: 1}
  }},
  {$sort: {count: -1}}
])
```

If you see many entries with `"reasoning": "System error..."`, then Ollama is consistently failing.

