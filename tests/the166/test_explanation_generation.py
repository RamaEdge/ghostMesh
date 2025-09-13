#!/usr/bin/env python3
"""
THE-166: AI Explainer Service - Explanation Generation Tests

This test module validates the core explanation generation functionality
of the AI Explainer service, including signal analysis, confidence scoring,
and explanation formatting.
"""

import json
import pytest
import sys
import os

# Add the explainer module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../explainer'))

from explainer import AIExplainer


class TestExplanationGeneration:
    """Test cases for explanation generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.explainer = AIExplainer()
    
    def test_temperature_anomaly_explanation(self):
        """Test explanation generation for temperature anomalies."""
        alert_id = "alert-001"
        asset_id = "Press01"
        signal = "Temperature"
        severity = "high"
        current_value = 45.2
        reason = "Statistical anomaly detected"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate explanation structure
        assert explanation['alertId'] == alert_id
        assert 'text' in explanation
        assert 'confidence' in explanation
        assert 'riskLevel' in explanation
        assert 'recommendedActions' in explanation
        assert 'ts' in explanation
        
        # Validate explanation content
        assert "Temperature anomaly" in explanation['text']
        assert "Press01" in explanation['text']
        assert "45.2°C" in explanation['text']
        assert "overheating" in explanation['text'].lower()
        
        # Validate confidence score
        assert 0.5 <= explanation['confidence'] <= 1.0
        
        # Validate risk level
        assert explanation['riskLevel'] == "high"
        
        # Validate recommendations
        assert "inspect_equipment" in explanation['recommendedActions']
        assert "check_cooling_system" in explanation['recommendedActions']
    
    def test_pressure_anomaly_explanation(self):
        """Test explanation generation for pressure anomalies."""
        alert_id = "alert-002"
        asset_id = "Valve03"
        signal = "Pressure"
        severity = "medium"
        current_value = 15.8
        reason = "Statistical anomaly detected"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate explanation content
        assert "Pressure anomaly" in explanation['text']
        assert "Valve03" in explanation['text']
        assert "15.8 bar" in explanation['text']
        assert "pressure" in explanation['text'].lower()
        
        # Validate risk level
        assert explanation['riskLevel'] == "medium"
        
        # Validate recommendations
        assert "check_for_leaks" in explanation['recommendedActions']
        assert "inspect_valves" in explanation['recommendedActions']
    
    def test_speed_anomaly_explanation(self):
        """Test explanation generation for speed anomalies."""
        alert_id = "alert-003"
        asset_id = "Conveyor01"
        signal = "Speed"
        severity = "low"
        current_value = 25.5
        reason = "Statistical anomaly detected"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate explanation content
        assert "Speed anomaly" in explanation['text']
        assert "Conveyor01" in explanation['text']
        assert "25.5 rpm" in explanation['text']
        assert "motor" in explanation['text'].lower()
        
        # Validate risk level
        assert explanation['riskLevel'] == "low"
        
        # Validate recommendations
        assert "inspect_motor" in explanation['recommendedActions']
        assert "check_mechanical_components" in explanation['recommendedActions']
    
    def test_vibration_anomaly_explanation(self):
        """Test explanation generation for vibration anomalies."""
        alert_id = "alert-004"
        asset_id = "Press02"
        signal = "Vibration"
        severity = "high"
        current_value = 3.2
        reason = "Statistical anomaly detected"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate explanation content
        assert "Vibration anomaly" in explanation['text']
        assert "Press02" in explanation['text']
        assert "3.2 mm/s" in explanation['text']
        assert "mechanical" in explanation['text'].lower()
        
        # Validate risk level
        assert explanation['riskLevel'] == "high"
        
        # Validate recommendations
        assert "inspect_bearings" in explanation['recommendedActions']
        assert "check_alignment" in explanation['recommendedActions']
    
    def test_unknown_signal_explanation(self):
        """Test explanation generation for unknown signal types."""
        alert_id = "alert-005"
        asset_id = "Sensor05"
        signal = "UnknownSignal"
        severity = "medium"
        current_value = 100.0
        reason = "Statistical anomaly detected"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate explanation content
        assert "UnknownSignal anomaly" in explanation['text']
        assert "Sensor05" in explanation['text']
        assert "100.0" in explanation['text']
        assert "malfunction" in explanation['text'].lower()
        
        # Validate recommendations
        assert "investigate_anomaly" in explanation['recommendedActions']
        assert "check_equipment_status" in explanation['recommendedActions']
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # Test different signal types
        signals = ["Temperature", "Pressure", "Speed", "Vibration"]
        severities = ["low", "medium", "high"]
        
        for signal in signals:
            for severity in severities:
                confidence = self.explainer._calculate_confidence(signal, severity, 50.0)
                assert 0.5 <= confidence <= 1.0, f"Confidence out of range for {signal}/{severity}: {confidence}"
    
    def test_asset_context(self):
        """Test asset context generation."""
        test_cases = [
            ("Press01", "hydraulic press"),
            ("Press02", "hydraulic press"),
            ("Conveyor01", "conveyor belt system"),
            ("Valve03", "control valve"),
            ("Sensor05", "environmental sensor"),
            ("UnknownAsset", "industrial equipment")
        ]
        
        for asset_id, expected_context in test_cases:
            context = self.explainer._get_asset_context(asset_id)
            assert context == expected_context, f"Unexpected context for {asset_id}: {context}"
    
    def test_signal_analysis(self):
        """Test signal analysis functionality."""
        # Test temperature analysis
        temp_analysis = self.explainer._analyze_signal("Temperature", 45.0, "high")
        assert "Temperature anomaly" in temp_analysis['description']
        assert "overheating" in temp_analysis['impact'].lower()
        assert "cooling" in temp_analysis['immediate_concern'].lower()
        assert "inspect_equipment" in temp_analysis['recommendations']
        
        # Test pressure analysis
        pressure_analysis = self.explainer._analyze_signal("Pressure", 15.0, "medium")
        assert "Pressure anomaly" in pressure_analysis['description']
        assert "pressure" in pressure_analysis['impact'].lower()
        assert "leaks" in pressure_analysis['immediate_concern'].lower()
        assert "check_for_leaks" in pressure_analysis['recommendations']
    
    def test_explanation_json_schema(self):
        """Test that explanations follow the correct JSON schema."""
        alert_id = "alert-schema-test"
        asset_id = "Press01"
        signal = "Temperature"
        severity = "high"
        current_value = 50.0
        reason = "Test anomaly"
        
        explanation = self.explainer._generate_explanation(
            alert_id, asset_id, signal, severity, current_value, reason
        )
        
        # Validate JSON serialization
        json_str = json.dumps(explanation)
        parsed = json.loads(json_str)
        assert parsed == explanation
        
        # Validate required fields
        required_fields = ['alertId', 'text', 'confidence', 'riskLevel', 'recommendedActions', 'ts']
        for field in required_fields:
            assert field in explanation, f"Missing required field: {field}"
        
        # Validate field types
        assert isinstance(explanation['alertId'], str)
        assert isinstance(explanation['text'], str)
        assert isinstance(explanation['confidence'], (int, float))
        assert isinstance(explanation['riskLevel'], str)
        assert isinstance(explanation['recommendedActions'], list)
        assert isinstance(explanation['ts'], str)
        
        # Validate field values
        assert len(explanation['text']) > 0
        assert 0.0 <= explanation['confidence'] <= 1.0
        assert explanation['riskLevel'] in ['low', 'medium', 'high']
        assert len(explanation['recommendedActions']) > 0


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
