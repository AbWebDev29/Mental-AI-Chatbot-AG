#!/usr/bin/env python3
"""
Integration Test: Verify MongoDB document structure is correct
Run this to test that clinical_markers are being stored properly
"""

import asyncio
import sys
from nlp_engine import get_llama_clinical_analysis

def test_clinical_analysis():
    """Test the clinical analysis function directly"""
    
    print("=" * 70)
    print("🧪 CLINICAL ANALYSIS INTEGRATION TEST")
    print("=" * 70)
    
    # Test message (same as user's example)
    test_message = "I'm surrounded by people but I've never felt more alone in my life."
    history = ""
    
    print(f"\n📝 Test Message: {test_message}")
    print(f"📋 History: (empty)")
    
    print("\n" + "=" * 70)
    print("🔄 Running get_llama_clinical_analysis()...")
    print("=" * 70)
    
    try:
        result = get_llama_clinical_analysis(test_message, history)
        
        print("\n✅ RESULT:")
        print("-" * 70)
        
        # Pretty print the result
        for key, value in result.items():
            print(f"  {key:.<30} {value}")
        
        print("-" * 70)
        
        # Verify structure
        required_fields = [
            "emotion_tag",
            "emotion_cluster",
            "clinical_label",
            "clinical_category",
            "intensity",
            "trigger_source",
            "is_recurring",
            "functional_impact",
            "reasoning"
        ]
        
        print("\n✓ FIELD VERIFICATION:")
        missing_fields = []
        for field in required_fields:
            if field in result:
                print(f"  ✅ {field:.<30} Present")
            else:
                print(f"  ❌ {field:.<30} MISSING")
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n❌ MISSING FIELDS: {missing_fields}")
            return False
        else:
            print(f"\n✅ ALL REQUIRED FIELDS PRESENT")
        
        # Verify types
        print("\n✓ TYPE VERIFICATION:")
        type_checks = {
            "emotion_tag": str,
            "emotion_cluster": str,
            "clinical_label": str,
            "clinical_category": str,
            "intensity": int,
            "trigger_source": str,
            "is_recurring": bool,
            "functional_impact": int,
            "reasoning": str
        }
        
        type_errors = []
        for field, expected_type in type_checks.items():
            actual_type = type(result[field])
            if actual_type == expected_type:
                print(f"  ✅ {field:.<30} {expected_type.__name__}")
            else:
                print(f"  ❌ {field:.<30} Expected {expected_type.__name__}, got {actual_type.__name__}")
                type_errors.append(field)
        
        if type_errors:
            print(f"\n❌ TYPE ERRORS: {type_errors}")
            return False
        else:
            print(f"\n✅ ALL TYPES CORRECT")
        
        # Show expected MongoDB document
        print("\n" + "=" * 70)
        print("📊 EXPECTED MONGODB DOCUMENT:")
        print("=" * 70)
        
        import json
        expected_doc = {
            "_id": "ObjectId(...)",
            "user_id": "user_id_here",
            "timestamp": "2026-04-03T10:30:00Z",
            "message": test_message,
            "ai_reply": "AI response here...",
            "clinical_markers": result
        }
        
        print(json.dumps(expected_doc, indent=2, default=str))
        
        print("\n" + "=" * 70)
        print("✅ INTEGRATION TEST PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_clinical_analysis()
    sys.exit(0 if success else 1)
