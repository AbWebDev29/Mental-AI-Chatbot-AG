#!/usr/bin/env python3
"""
Diagnostic: Check why clinical analysis is defaulting to "System error"
"""

import json
import sys
import ollama
from taxonomy import get_full_taxonomy_string, TRIGGER_SOURCES

def test_ollama_connection():
    """Test if Ollama is running"""
    print("=" * 70)
    print("🔍 TESTING OLLAMA CONNECTION")
    print("=" * 70)
    
    try:
        # Try to list available models
        response = ollama.list()
        print(f"✅ Ollama is running")
        print(f"Available models: {response}")
        return True
    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print(f"\n💡 Fix: Run `ollama serve` in another terminal")
        return False


def test_json_mode():
    """Test if JSON mode works"""
    print("\n" + "=" * 70)
    print("🧪 TESTING JSON MODE WITH LLAMA 3.2 3B")
    print("=" * 70)
    
    try:
        # Simple test message
        response = ollama.chat(
            model="llama3.2:3b",
            format="json",
            messages=[
                {
                    "role": "user",
                    "content": 'Respond only with JSON. {"test": "works"}'
                }
            ],
            options={"temperature": 0.3}
        )
        
        response_text = response["message"]["content"].strip()
        print(f"✅ JSON Mode Test Response:\n{response_text}")
        
        # Try to parse it
        try:
            parsed = json.loads(response_text)
            print(f"\n✅ Response is valid JSON")
            return True
        except json.JSONDecodeError as e:
            print(f"\n❌ Response is NOT valid JSON: {e}")
            print(f"Raw: {response_text}")
            return False
            
    except Exception as e:
        print(f"❌ JSON Mode test failed: {e}")
        return False


def test_clinical_analysis():
    """Test the actual clinical analysis"""
    print("\n" + "=" * 70)
    print("🧬 TESTING CLINICAL ANALYSIS")
    print("=" * 70)
    
    test_message = "I'm surrounded by people but I've never felt more alone in my life."
    
    print(f"Test message: {test_message}\n")
    
    # Build the system prompt
    system_prompt = f"""
You are a Clinical NLP Classification System. Your role is to analyze the user's mental and emotional state and map it to a specific taxonomy.

CRITICAL RULES:
1. You MUST respond with ONLY valid JSON (no markdown, no explanation)
2. You MUST choose emotions ONLY from the provided emotion list
3. You MUST choose clinical conditions ONLY from the provided condition list
4. If an emotion/condition isn't an exact match, find the closest one from the lists
5. Intensity must be a number between 1-10
6. Provide clear, clinical reasoning

{get_full_taxonomy_string()}

CURRENT CONTEXT:
(No previous conversation)

YOUR TASK:
Analyze the user's message and extract:
1. The most accurate emotion (from the 100+ list above)
2. The most relevant mental health condition (from the 50+ list above)
3. The emotion cluster (JOY, SADNESS, ANGER, FEAR, SHAME, COMPLEX)
4. The condition category (ANXIETY, MOOD, TRAUMA, etc.)
5. Intensity rating (1-10): How severe is their current distress?
6. Primary trigger source (from the list: {', '.join(TRIGGER_SOURCES)})
7. Is this a recurring pattern or new symptom? (boolean)
8. Functional impact (1-10): How much is this affecting their daily life?

RESPONSE SCHEMA (STRICT JSON ONLY):
{{
  "emotion": "string (MUST be from emotion list)",
  "emotion_cluster": "string (JOY/SADNESS/ANGER/FEAR/SHAME/COMPLEX)",
  "clinical_condition": "string (MUST be from condition list)",
  "condition_category": "string (ANXIETY/MOOD/TRAUMA/etc)",
  "intensity": number (1-10),
  "trigger_source": "string (from trigger sources list)",
  "is_recurring": boolean,
  "functional_impact": number (1-10),
  "reasoning": "string (brief 1-sentence explanation)"
}}

Remember: ONLY JSON output. NO other text.
"""
    
    try:
        print("📡 Calling Ollama with JSON mode...\n")
        
        response = ollama.chat(
            model="llama3.2:3b",
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this mental health statement: {test_message}"
                }
            ],
            options={
                "temperature": 0.3,
                "num_ctx": 4096
            }
        )
        
        response_text = response["message"]["content"].strip()
        print(f"Response from Ollama:\n{response_text}\n")
        
        # Try to parse
        try:
            analysis = json.loads(response_text)
            print(f"✅ Successfully parsed as JSON")
            print(f"\nAnalysis:")
            for key, value in analysis.items():
                print(f"  {key:.<30} {value}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 70)
    print("🔧 CLINICAL ANALYSIS DIAGNOSTIC")
    print("=" * 70 + "\n")
    
    results = []
    
    # Test 1: Ollama connection
    if not test_ollama_connection():
        print("\n❌ DIAGNOSTIC FAILED: Ollama not running")
        print("Fix: Run `ollama serve` in another terminal, then retry this diagnostic")
        return False
    
    # Test 2: JSON mode
    if not test_json_mode():
        print("\n⚠️ WARNING: JSON mode test failed")
        print("This might be a model-specific issue")
    
    # Test 3: Clinical analysis
    if not test_clinical_analysis():
        print("\n❌ DIAGNOSTIC FAILED: Clinical analysis not working")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL DIAGNOSTIC TESTS PASSED")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("  1. Restart your backend server: uvicorn main:app --reload")
    print("  2. Make a new chat request")
    print("  3. Check MongoDB for clinical_markers with proper structure")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
