# 🎬 ACTION PLAN: Next 15 Minutes

## Current Status
✅ Chat system working beautifully
❌ Taxonomy system stuck (all messages showing "Overwhelmed/GAD/System error")

---

## The Fix (3 Easy Steps)

### Step 1️⃣: DIAGNOSE (2 minutes)
```bash
cd /Users/anvibansal/mental-app/backend
python diagnose_ollama.py
```

**You'll see ONE of these:**

**Option A: ✅ All tests pass**
→ Ollama IS working, something else wrong (see Step 2)

**Option B: ❌ Ollama connection fails**
→ Run this: `ollama serve` (in another terminal)

**Option C: ❌ JSON mode test fails**
→ Check line 112 in `clinical_analyzer_llama.py` has `format="json"`

---

### Step 2️⃣: FIX (5 minutes)
Based on diagnostic output, apply fix from:

📖 **File:** `TROUBLESHOOTING_SYSTEM_ERROR.md`

**Most common fix:**
```bash
# Ensure Ollama is running
ollama serve

# Then restart backend
cd /Users/anvibansal/mental-app/backend
uvicorn main:app --reload
```

---

### Step 3️⃣: VERIFY (2 minutes)
```bash
# Make test request
curl "http://localhost:8000/chat?user_id=test&message=I%20feel%20so%20alone"

# Then check MongoDB Compass:
# - Open collections > sessions
# - Look at latest document
# - Check clinical_markers
```

**Should show:**
```json
{
  "emotion_tag": "Alienated",          ✅ (NOT "Overwhelmed")
  "clinical_label": "Social Anxiety",  ✅ (NOT "GAD")
  "intensity": 8,                      ✅ (NOT 5)
  "reasoning": "User feels isolated..." ✅ (NOT "System error")
}
```

---

## Then: Monthly Reports (1 minute setup)

**File:** `backend/monthly_report_queries.py`

**Usage:**
```python
from monthly_report_queries import generate_monthly_report

# Generate complete monthly report
report = await generate_monthly_report(db, user_id)

# Returns structured data with:
# - Top emotions
# - Clinical conditions
# - Triggers
# - Functional impact trend
# - Crisis episodes
# - Recurring patterns
```

**8 queries are ready to use:**
1. Emotion frequency
2. Clinical conditions
3. Trigger analysis
4. Functional impact trend
5. Emotion clusters
6. Clinical categories
7. High-intensity episodes
8. Recurring patterns

---

## 📊 What You Get

After fixing the taxonomy system:

### Daily Insights
```
"Today's message shows: Alienated / Social Anxiety (intensity 8)"
(Not just: Overwhelmed / GAD / System error)
```

### Monthly Reports
```
Top emotions: Alienated (15%), Overwhelmed (13%), Petrified (10%)
Top conditions: Social Anxiety (10%), MDD (9%), Panic Disorder (8%)
Main triggers: Social Disconnection (19%), Work Stress (15%)
Functional impact: 6.5 → 5.2 (IMPROVING! 📈)
```

### Crisis Detection
```
High-intensity episodes (intensity >= 8): 2 this month
Last crisis: April 2, 14:30 - triggered by work stress
```

### Recurring Patterns
```
Pattern: Alienated → Social Anxiety → Every 2-3 days
Pattern: Overwhelmed → MDD → After poor sleep nights
```

---

## 🎯 Timeline

| Time | Task | Status |
|------|------|--------|
| 0:00-2:00 | Run diagnostic | 🔄 Do this now |
| 2:00-7:00 | Apply fix | 🔄 Based on diagnostic |
| 7:00-9:00 | Verify working | 🔄 Check MongoDB |
| 9:00-15:00 | Generate reports | ✅ Ready to use |

**Total: 15 minutes to full deployment** ⏱️

---

## 📁 Reference Files

**Main files:**
- `TROUBLESHOOTING_SYSTEM_ERROR.md` - All fixes for taxonomy issues
- `backend/monthly_report_queries.py` - 8 ready-to-use MongoDB queries
- `backend/monthly_report_generator.py` - Report formatting
- `COMPLETE_STATUS_REPORT.md` - Full overview

**Diagnostic:**
- `backend/diagnose_ollama.py` - Run this first!

**Examples:**
- `MONGODB_EXAMPLES.md` - 10 real document examples
- `INTEGRATION_VERIFICATION.md` - Before/after code changes

---

## ✅ Checkpoints

**After Step 1 (Diagnose):**
- [ ] Diagnostic runs without crashing
- [ ] Shows clear pass/fail for each test

**After Step 2 (Fix):**
- [ ] Ollama running: `ollama list` shows llama3.2:3b
- [ ] Backend restarted: `uvicorn main:app --reload` running

**After Step 3 (Verify):**
- [ ] MongoDB shows emotion != "Overwhelmed"
- [ ] MongoDB shows condition != "GAD"
- [ ] MongoDB reasoning != "System error"

**After Reports (Deploy):**
- [ ] Can generate monthly reports
- [ ] Reports show variety (not all same values)
- [ ] Trends visible in functional_impact_trend

---

## 🚨 If Stuck

**Issue:** Diagnostic fails
→ Check: Is Ollama installed? `brew list | grep ollama`

**Issue:** Still seeing "System error" after fix
→ Check: `TROUBLESHOOTING_SYSTEM_ERROR.md` for advanced fixes

**Issue:** Reports show no data
→ Check: `MONGODB_EXAMPLES.md` for query examples

**Issue:** MongoDB queries not working
→ Check: `monthly_report_queries.py` for syntax

---

## 📞 Quick Reference

```bash
# Start Ollama
ollama serve

# Check Ollama
ollama list

# Run diagnostic
python diagnose_ollama.py

# Run backend
uvicorn main:app --reload

# Check logs
uvicorn main:app --reload --log-level DEBUG

# Make test request
curl "http://localhost:8000/chat?user_id=test&message=test"
```

---

## 🎉 Success = 

✅ Taxonomy working (different emotions for different messages)
✅ No more "System error" (clinical reasoning shown)
✅ Monthly reports generating (tracking user progress)
✅ Insights visible (can see trends and patterns)

---

## 🚀 Ready?

**Next action:**
```bash
cd /Users/anvibansal/mental-app/backend
python diagnose_ollama.py
```

This takes 30-60 seconds and tells you exactly what to fix! 💪
