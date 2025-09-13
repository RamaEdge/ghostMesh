#!/usr/bin/env python3
"""
THE-67: LLM Integration Tests

Tests for the LLM-powered explainer service integration.
"""

import json
import sys
import os
import time
import requests
from datetime import datetime, timezone

# Add the explainer directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../explainer'))

from llm_service import LLMService, LLMConfig

def test_llm_service_initialization():
    """Test LLM service initialization."""
    print("Testing LLM service initialization...")
    
    config = LLMConfig(server_url="http://localhost:8080")
    service = LLMService(config)
    
    assert service is not None
    print("✓ LLM service initialized successfully")
    
    return service

def test_prompt_templates():
    """Test prompt template availability."""
    print("Testing prompt templates...")
    
    service = LLMService()
    templates = service.get_available_templates()
    
    expected_templates = ["operator", "analyst", "hybrid"]
    for template in expected_templates:
        assert template in templates, f"Template {template} not found"
    
    print(f"✓ Available templates: {templates}")
    return service

def test_llm_server_availability():
    """Test LLM server availability."""
    print("Testing LLM server availability...")
    
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✓ LLM server is available")
            return True
        else:
            print(f"✗ LLM server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ LLM server not available: {e}")
        return False

def test_explanation_generation():
    """Test explanation generation with different user types."""
    print("Testing explanation generation...")
    
    service = LLMService()
    
    # Test alert data
    test_alert = {
        "alertId": "test-123",
        "assetId": "press01",
        "signal": "temperature",
        "severity": "high",
        "current": 85.5,
        "reason": "z-score 8.2 vs mean 35.0±2.1 (120s)",
        "ts": datetime.now(timezone.utc).isoformat()
    }
    
    # Test different user types
    user_types = ["operator", "analyst", "hybrid"]
    
    for user_type in user_types:
        print(f"  Testing {user_type} explanation...")
        explanation = service.generate_explanation(test_alert, user_type)
        
        # Validate explanation structure
        assert "alertId" in explanation
        assert "text" in explanation
        assert "confidence" in explanation
        assert "riskLevel" in explanation
        assert "userType" in explanation
        assert "recommendations" in explanation
        assert "ts" in explanation
        assert "source" in explanation
        
        # Validate values
        assert explanation["alertId"] == test_alert["alertId"]
        assert explanation["userType"] == user_type
        assert 0.0 <= explanation["confidence"] <= 1.0
        assert explanation["source"] in ["llm", "fallback"]
        
        print(f"    ✓ {user_type} explanation generated (confidence: {explanation['confidence']:.2f})")
    
    print("✓ All explanation types generated successfully")
    return True

def test_fallback_explanation():
    """Test fallback explanation when LLM is not available."""
    print("Testing fallback explanation...")
    
    # Create service with invalid server URL to force fallback
    config = LLMConfig(server_url="http://invalid-server:8080")
    service = LLMService(config)
    
    test_alert = {
        "alertId": "fallback-test",
        "assetId": "press02",
        "signal": "pressure",
        "severity": "medium",
        "current": 150.0,
        "reason": "z-score 4.5 vs mean 145.0±2.0 (120s)",
        "ts": datetime.now(timezone.utc).isoformat()
    }
    
    explanation = service.generate_explanation(test_alert, "operator")
    
    # Validate fallback explanation
    assert explanation["source"] == "fallback"
    assert explanation["confidence"] == 0.5
    assert "investigate" in explanation["text"].lower()
    assert len(explanation["recommendations"]) > 0
    
    print("✓ Fallback explanation generated successfully")
    return True

def test_confidence_calculation():
    """Test confidence calculation logic."""
    print("Testing confidence calculation...")
    
    service = LLMService()
    
    # Test with different explanation qualities
    test_cases = [
        {
            "text": "Short explanation",
            "alert_data": {"current": 100, "assetId": "test"},
            "expected_min": 0.5,
            "expected_max": 0.8
        },
        {
            "text": "This is a very detailed explanation that mentions the specific value 100 and the asset test. It provides comprehensive analysis and actionable recommendations.",
            "alert_data": {"current": 100, "assetId": "test"},
            "expected_min": 0.8,
            "expected_max": 0.95
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        confidence = service._calculate_confidence(test_case["text"], test_case["alert_data"])
        assert test_case["expected_min"] <= confidence <= test_case["expected_max"], \
            f"Confidence {confidence} not in expected range for test case {i+1}"
        print(f"  ✓ Test case {i+1}: confidence = {confidence:.2f}")
    
    print("✓ Confidence calculation working correctly")
    return True

def test_risk_level_extraction():
    """Test risk level extraction from explanations."""
    print("Testing risk level extraction...")
    
    service = LLMService()
    
    test_cases = [
        {
            "text": "This is a critical situation requiring immediate attention",
            "severity": "medium",
            "expected": "high"
        },
        {
            "text": "This is a concerning anomaly that needs investigation",
            "severity": "low",
            "expected": "medium"
        },
        {
            "text": "Normal operation with minor variations",
            "severity": "high",
            "expected": "high"  # Should default to alert severity
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        risk_level = service._extract_risk_level(test_case["text"], test_case["severity"])
        assert risk_level == test_case["expected"], \
            f"Risk level {risk_level} not expected {test_case['expected']} for test case {i+1}"
        print(f"  ✓ Test case {i+1}: risk level = {risk_level}")
    
    print("✓ Risk level extraction working correctly")
    return True

def main():
    """Run all LLM integration tests."""
    print("=" * 60)
    print("THE-67: LLM Integration Tests")
    print("=" * 60)
    
    tests = [
        test_llm_service_initialization,
        test_prompt_templates,
        test_llm_server_availability,
        test_explanation_generation,
        test_fallback_explanation,
        test_confidence_calculation,
        test_risk_level_extraction
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
