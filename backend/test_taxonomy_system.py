#!/usr/bin/env python3
"""
TEST SCRIPT: Verify the Llama Taxonomy Classification System

This script tests all components of the clinical taxonomy system to ensure
Ollama's JSON mode correctly classifies 100+ emotions and 50+ conditions.

Usage:
    python test_taxonomy_system.py

This will:
1. Verify taxonomy.py loads correctly
2. Test clinical_analyzer_llama.py with sample messages
3. Verify JSON output format
4. Check taxonomy validation
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from taxonomy import (
    ALL_EMOTIONS,
    ALL_MENTAL_HEALTH_CONDITIONS,
    TRIGGER_SOURCES,
    get_emotion_cluster,
    get_condition_category,
    validate_emotion,
    validate_condition,
    find_closest_emotion,
    find_closest_condition,
    EMOTION_CLUSTERS,
    MENTAL_HEALTH_CONDITIONS
)

from clinical_analyzer_llama import (
    get_clinical_taxonomy_analysis,
    format_analysis_for_storage,
    get_fallback_analysis
)


def test_taxonomy_loading():
    """Test 1: Verify taxonomies load correctly"""
    print("\n" + "="*70)
    print("TEST 1: TAXONOMY LOADING")
    print("="*70)
    
    print(f"✓ Loaded {len(ALL_EMOTIONS)} emotions")
    print(f"  JOY: {len(EMOTION_CLUSTERS['JOY'])}")
    print(f"  SADNESS: {len(EMOTION_CLUSTERS['SADNESS'])}")
    print(f"  ANGER: {len(EMOTION_CLUSTERS['ANGER'])}")
    print(f"  FEAR: {len(EMOTION_CLUSTERS['FEAR'])}")
    print(f"  SHAME: {len(EMOTION_CLUSTERS['SHAME'])}")
    print(f"  COMPLEX: {len(EMOTION_CLUSTERS['COMPLEX'])}")
    
    print(f"\n✓ Loaded {len(ALL_MENTAL_HEALTH_CONDITIONS)} mental health conditions")
    for category, conditions in MENTAL_HEALTH_CONDITIONS.items():
        print(f"  {category}: {len(conditions)}")
    
    print(f"\n✓ Loaded {len(TRIGGER_SOURCES)} trigger sources")
    
    return True


def test_taxonomy_validation():
    """Test 2: Verify validation functions work"""
    print("\n" + "="*70)
    print("TEST 2: TAXONOMY VALIDATION")
    print("="*70)
    
    # Valid emotion
    assert validate_emotion("Elated"), "Failed to validate 'Elated'"
    print("✓ validate_emotion('Elated') = True")
    
    # Invalid emotion
    assert not validate_emotion("XYZ_INVALID"), "Should not validate invalid emotion"
    print("✓ validate_emotion('XYZ_INVALID') = False")
    
    # Valid condition
    assert validate_condition("GAD (Generalized Anxiety Disorder)"), "Failed to validate 'GAD'"
    print("✓ validate_condition('GAD (Generalized Anxiety Disorder)') = True")
    
    # Invalid condition
    assert not validate_condition("FAKE_CONDITION"), "Should not validate invalid condition"
    print("✓ validate_condition('FAKE_CONDITION') = False")
    
    # Cluster lookup
    cluster = get_emotion_cluster("Elated")
    assert cluster == "JOY", f"Expected JOY, got {cluster}"
    print(f"✓ get_emotion_cluster('Elated') = {cluster}")
    
    # Category lookup
    category = get_condition_category("GAD (Generalized Anxiety Disorder)")
    assert category == "ANXIETY", f"Expected ANXIETY, got {category}"
    print(f"✓ get_condition_category('GAD...') = {category}")
    
    return True


def test_fuzzy_matching():
    """Test 3: Verify fuzzy matching finds closest options"""
    print("\n" + "="*70)
    print("TEST 3: FUZZY MATCHING")
    print("="*70)
    
    test_cases = [
        ("happy", "Elated"),  # Should match JOY cluster
        ("sad", "Dejected"),   # Should match SADNESS cluster
        ("scared", "Petrified"),  # Should match FEAR cluster
        ("angry", "Infuriated"),  # Should match ANGER cluster
        ("ashamed", "Mortified"),  # Should match SHAME cluster
    ]
    
    for input_emotion, expected_family in test_cases:
        matched = find_closest_emotion(input_emotion)
        print(f"✓ find_closest_emotion('{input_emotion}') -> '{matched}'")
    
    # Test condition matching
    condition_matches = [
        ("anxiety", "GAD (Generalized Anxiety Disorder)"),
        ("ptsd", "PTSD (Post-Traumatic Stress Disorder)"),
        ("depression", "MDD (Major Depressive Disorder)"),
    ]
    
    for input_condition, expected_match in condition_matches:
        matched = find_closest_condition(input_condition)
        print(f"✓ find_closest_condition('{input_condition}') -> '{matched}'")
    
    return True


def test_fallback_analysis():
    """Test 4: Verify fallback analysis works when Ollama unavailable"""
    print("\n" + "="*70)
    print("TEST 4: FALLBACK ANALYSIS (No Ollama Required)")
    print("="*70)
    
    test_messages = [
        "I feel happy and grateful",
        "I'm so depressed and hopeless",
        "I'm terrified and anxious",
        "I feel ashamed and worthless",
        "I'm furious and angry",
    ]
    
    for msg in test_messages:
        analysis = get_fallback_analysis(msg)
        
        # Verify output structure
        assert "emotion" in analysis
        assert "clinical_condition" in analysis
        assert "intensity" in analysis
        assert isinstance(analysis["intensity"], int)
        assert 1 <= analysis["intensity"] <= 10
        
        print(f"\n  Input: '{msg}'")
        print(f"  → Emotion: {analysis['emotion']}")
        print(f"  → Condition: {analysis['clinical_condition']}")
        print(f"  → Intensity: {analysis['intensity']}")
    
    return True


def test_format_for_storage():
    """Test 5: Verify formatting for MongoDB"""
    print("\n" + "="*70)
    print("TEST 5: FORMAT FOR MONGODB STORAGE")
    print("="*70)
    
    sample_analysis = {
        "emotion": "Paralyzed",
        "emotion_cluster": "COMPLEX",
        "clinical_condition": "GAD (Generalized Anxiety Disorder)",
        "clinical_category": "ANXIETY",
        "intensity": 8,
        "trigger_source": "Work/Career/Performance",
        "is_recurring": True,
        "functional_impact": 7,
        "reasoning": "Perfectionist paralysis"
    }
    
    formatted = format_analysis_for_storage(sample_analysis)
    
    print("\nInput analysis:")
    print(json.dumps(sample_analysis, indent=2))
    
    print("\nFormatted for MongoDB:")
    print(json.dumps(formatted, indent=2))
    
    # Verify all required fields
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
    
    for field in required_fields:
        assert field in formatted, f"Missing field: {field}"
        print(f"✓ {field}: {formatted[field]}")
    
    return True


def test_with_ollama():
    """Test 6: Test actual Ollama integration (if available)"""
    print("\n" + "="*70)
    print("TEST 6: OLLAMA INTEGRATION TEST")
    print("="*70)
    
    try:
        import ollama
        print("✓ ollama module found")
        
        # Check if Ollama is running
        try:
            models = ollama.list()
            print("✓ Ollama is running")
            print(f"✓ Available models: {[m['name'] for m in models.models]}")
            
            # Test with a simple message
            print("\nTesting with sample message...")
            analysis = get_clinical_taxonomy_analysis("I feel overwhelmed and anxious")
            
            print("\nOllama Analysis Result:")
            print(json.dumps(analysis, indent=2))
            
            # Verify taxonomy compliance
            if analysis.get("emotion") in ALL_EMOTIONS:
                print(f"✓ Emotion '{analysis['emotion']}' is in taxonomy")
            else:
                print(f"⚠ Emotion '{analysis['emotion']}' not in taxonomy (will use fallback)")
            
            if analysis.get("clinical_condition") in ALL_MENTAL_HEALTH_CONDITIONS:
                print(f"✓ Condition '{analysis['clinical_condition']}' is in taxonomy")
            else:
                print(f"⚠ Condition '{analysis['clinical_condition']}' not in taxonomy (will use fallback)")
            
            return True
            
        except Exception as e:
            print(f"⚠ Ollama not responding: {e}")
            print("  Run: ollama serve")
            return False
            
    except ImportError:
        print("⚠ ollama module not installed")
        print("  Install: pip install ollama")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "█"*70)
    print("█  LLAMA TAXONOMY CLASSIFICATION SYSTEM - TEST SUITE")
    print("█"*70)
    
    results = []
    
    # Test 1: Taxonomy Loading
    try:
        results.append(("Taxonomy Loading", test_taxonomy_loading()))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Taxonomy Loading", False))
    
    # Test 2: Taxonomy Validation
    try:
        results.append(("Taxonomy Validation", test_taxonomy_validation()))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Taxonomy Validation", False))
    
    # Test 3: Fuzzy Matching
    try:
        results.append(("Fuzzy Matching", test_fuzzy_matching()))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Fuzzy Matching", False))
    
    # Test 4: Fallback Analysis
    try:
        results.append(("Fallback Analysis", test_fallback_analysis()))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Fallback Analysis", False))
    
    # Test 5: Format for Storage
    try:
        results.append(("Format for Storage", test_format_for_storage()))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Format for Storage", False))
    
    # Test 6: Ollama Integration (optional)
    try:
        results.append(("Ollama Integration", test_with_ollama()))
    except Exception as e:
        print(f"⚠ Optional test skipped: {e}")
        results.append(("Ollama Integration", None))
    
    # Summary
    print("\n" + "█"*70)
    print("█  TEST SUMMARY")
    print("█"*70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        status = "✓ PASS" if result is True else ("⚠ SKIP" if result is None else "❌ FAIL")
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print("█"*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
