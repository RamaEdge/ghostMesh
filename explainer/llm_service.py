#!/usr/bin/env python3
"""
LLM Service for GhostMesh AI Explainer
Integrates with llama.cpp for local LLM inference

This module provides LLM integration for generating intelligent explanations
of security alerts using local language models.
"""

import json
import logging
import os
import requests
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM service."""
    model_path: str = "/models/qwen-0.5b-instruct.gguf"
    server_url: str = "http://localhost:8080"
    max_tokens: int = 512
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class PromptTemplate:
    """Prompt template for different user types."""
    name: str
    system_prompt: str
    user_prompt_template: str
    max_tokens: int = 256
    temperature: float = 0.7

class LLMService:
    """Service for interacting with local LLM via llama.cpp server."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM service with configuration."""
        self.config = config or LLMConfig()
        self.prompt_templates = self._initialize_prompt_templates()
        self.server_available = False
        self._check_server_availability()
    
    def _initialize_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize prompt templates for different user types."""
        return {
            "operator": PromptTemplate(
                name="operator",
                system_prompt="""You are an AI assistant helping industrial operators understand security alerts. 
Provide clear, actionable explanations that help operators make quick decisions. 
Focus on immediate actions and safety implications. Keep explanations concise and practical.""",
                user_prompt_template="""Analyze this security alert and provide a clear explanation for an industrial operator:

Alert Details:
- Asset: {asset_id}
- Signal: {signal}
- Severity: {severity}
- Current Value: {current_value} {unit}
- Reason: {reason}
- Timestamp: {timestamp}

Provide:
1. What this alert means in simple terms
2. Immediate safety concerns
3. Recommended actions
4. When to escalate

Explanation:""",
                max_tokens=200,
                temperature=0.6
            ),
            
            "analyst": PromptTemplate(
                name="analyst",
                system_prompt="""You are an AI assistant helping security analysts understand industrial alerts. 
Provide detailed technical explanations with context about potential attack vectors, 
statistical analysis, and forensic implications. Include confidence assessments and 
recommendations for further investigation.""",
                user_prompt_template="""Analyze this industrial security alert from a technical perspective:

Alert Details:
- Asset: {asset_id}
- Signal: {signal}
- Severity: {severity}
- Current Value: {current_value} {unit}
- Reason: {reason}
- Timestamp: {timestamp}
- Alert ID: {alert_id}

Provide detailed analysis including:
1. Technical explanation of the anomaly
2. Potential attack vectors or failure modes
3. Statistical significance and confidence
4. Forensic implications and evidence
5. Recommended investigation steps
6. Risk assessment and mitigation strategies

Technical Analysis:""",
                max_tokens=400,
                temperature=0.7
            ),
            
            "hybrid": PromptTemplate(
                name="hybrid",
                system_prompt="""You are an AI assistant helping both operators and analysts understand security alerts. 
Provide explanations that are technically accurate but accessible to different audiences. 
Balance detail with clarity, and include both immediate actions and deeper analysis.""",
                user_prompt_template="""Analyze this industrial security alert:

Alert Details:
- Asset: {asset_id}
- Signal: {signal}
- Severity: {severity}
- Current Value: {current_value} {unit}
- Reason: {reason}
- Timestamp: {timestamp}

Provide a comprehensive explanation including:
1. Executive Summary (what happened)
2. Technical Details (why it happened)
3. Immediate Actions (what to do now)
4. Risk Assessment (potential impact)
5. Recommendations (next steps)

Explanation:""",
                max_tokens=300,
                temperature=0.65
            )
        }
    
    def _check_server_availability(self) -> bool:
        """Check if llama.cpp server is available."""
        try:
            response = requests.get(
                f"{self.config.server_url}/health",
                timeout=5
            )
            self.server_available = response.status_code == 200
            if self.server_available:
                logger.info("LLM server is available")
            else:
                logger.warning(f"LLM server returned status {response.status_code}")
        except Exception as e:
            self.server_available = False
            logger.warning(f"LLM server not available: {e}")
        
        return self.server_available
    
    def _make_llm_request(self, prompt: str, template: PromptTemplate) -> Optional[str]:
        """Make request to llama.cpp server."""
        if not self.server_available:
            logger.error("LLM server not available")
            return None
        
        payload = {
            "prompt": prompt,
            "max_tokens": template.max_tokens,
            "temperature": template.temperature,
            "stop": ["\n\n", "Human:", "Assistant:"]
        }
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = requests.post(
                    f"{self.config.server_url}/completion",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("content", "").strip()
                else:
                    logger.warning(f"LLM request failed with status {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"LLM request attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
        
        logger.error("All LLM request attempts failed")
        return None
    
    def generate_explanation(self, alert_data: Dict[str, Any], user_type: str = "hybrid") -> Dict[str, Any]:
        """Generate explanation for an alert using LLM."""
        if not self.server_available:
            return self._generate_fallback_explanation(alert_data)
        
        template = self.prompt_templates.get(user_type, self.prompt_templates["hybrid"])
        
        # Prepare context for the prompt
        context = {
            "alert_id": alert_data.get("alertId", "unknown"),
            "asset_id": alert_data.get("assetId", "unknown"),
            "signal": alert_data.get("signal", "unknown"),
            "severity": alert_data.get("severity", "unknown"),
            "current_value": alert_data.get("current", 0),
            "unit": self._get_signal_unit(alert_data.get("signal", "")),
            "reason": alert_data.get("reason", "No reason provided"),
            "timestamp": alert_data.get("ts", "unknown")
        }
        
        # Format the user prompt
        user_prompt = template.user_prompt_template.format(**context)
        
        # Create full prompt with system message
        full_prompt = f"{template.system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
        
        # Generate explanation
        explanation_text = self._make_llm_request(full_prompt, template)
        
        if explanation_text:
            return self._format_explanation_response(alert_data, explanation_text, user_type)
        else:
            return self._generate_fallback_explanation(alert_data)
    
    def _get_signal_unit(self, signal: str) -> str:
        """Get unit for signal type."""
        units = {
            "temperature": "°C",
            "pressure": "bar",
            "speed": "rpm",
            "vibration": "mm/s",
            "flow": "L/min",
            "level": "%",
            "voltage": "V",
            "current": "A"
        }
        return units.get(signal.lower(), "units")
    
    def _format_explanation_response(self, alert_data: Dict[str, Any], explanation_text: str, user_type: str) -> Dict[str, Any]:
        """Format the LLM response into the expected explanation schema."""
        # Calculate confidence based on explanation quality
        confidence = self._calculate_confidence(explanation_text, alert_data)
        
        # Extract risk level from explanation
        risk_level = self._extract_risk_level(explanation_text, alert_data.get("severity", "medium"))
        
        # Generate recommendations
        recommendations = self._extract_recommendations(explanation_text)
        
        return {
            "alertId": alert_data.get("alertId"),
            "text": explanation_text,
            "confidence": confidence,
            "riskLevel": risk_level,
            "userType": user_type,
            "recommendations": recommendations,
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "llm"
        }
    
    def _calculate_confidence(self, explanation_text: str, alert_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on explanation quality."""
        base_confidence = 0.7
        
        # Increase confidence for longer, more detailed explanations
        if len(explanation_text) > 200:
            base_confidence += 0.1
        
        # Increase confidence for explanations that mention specific values
        if str(alert_data.get("current", "")) in explanation_text:
            base_confidence += 0.1
        
        # Increase confidence for explanations that mention the asset
        if alert_data.get("assetId", "").lower() in explanation_text.lower():
            base_confidence += 0.05
        
        # Increase confidence for explanations with action words
        action_words = ["isolate", "check", "monitor", "investigate", "escalate", "verify"]
        if any(word in explanation_text.lower() for word in action_words):
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)  # Cap at 95%
    
    def _extract_risk_level(self, explanation_text: str, alert_severity: str) -> str:
        """Extract risk level from explanation text."""
        text_lower = explanation_text.lower()
        
        # High risk indicators
        high_risk_indicators = ["critical", "urgent", "immediate", "danger", "threat", "attack", "compromise"]
        if any(indicator in text_lower for indicator in high_risk_indicators):
            return "high"
        
        # Medium risk indicators
        medium_risk_indicators = ["concerning", "suspicious", "unusual", "abnormal", "investigate"]
        if any(indicator in text_lower for indicator in medium_risk_indicators):
            return "medium"
        
        # Default to alert severity if no clear indicators
        return alert_severity.lower()
    
    def _extract_recommendations(self, explanation_text: str) -> List[str]:
        """Extract recommendations from explanation text."""
        recommendations = []
        lines = explanation_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and any(word in line.lower() for word in ["recommend", "suggest", "should", "action", "check", "monitor"]):
                # Clean up the recommendation
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    line = line[1:].strip()
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _generate_fallback_explanation(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback explanation when LLM is not available."""
        asset_id = alert_data.get("assetId", "unknown")
        signal = alert_data.get("signal", "unknown")
        severity = alert_data.get("severity", "medium")
        current_value = alert_data.get("current", 0)
        
        # Simple fallback explanation
        explanation_text = f"Alert detected on {asset_id} for {signal} signal. "
        explanation_text += f"Current value is {current_value}, which triggered a {severity} severity alert. "
        explanation_text += "Please investigate the anomaly and take appropriate action based on your operational procedures."
        
        return {
            "alertId": alert_data.get("alertId"),
            "text": explanation_text,
            "confidence": 0.5,
            "riskLevel": severity.lower(),
            "userType": "fallback",
            "recommendations": [
                "Investigate the anomaly",
                "Check system logs",
                "Verify sensor readings",
                "Follow operational procedures"
            ],
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "fallback"
        }
    
    def get_available_templates(self) -> List[str]:
        """Get list of available prompt templates."""
        return list(self.prompt_templates.keys())
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.server_available


def main():
    """Test the LLM service."""
    import sys
    
    # Test configuration
    config = LLMConfig(
        server_url="http://localhost:8080"
    )
    
    service = LLMService(config)
    
    # Test alert data
    test_alert = {
        "alertId": "test-123",
        "assetId": "press01",
        "signal": "temperature",
        "severity": "high",
        "current": 85.5,
        "reason": "z-score 8.2 vs mean 35.0±2.1 (120s)",
        "ts": "2025-09-13T15:00:00Z"
    }
    
    print(f"LLM Service Available: {service.is_available()}")
    print(f"Available Templates: {service.get_available_templates()}")
    
    # Test explanation generation
    for user_type in ["operator", "analyst", "hybrid"]:
        print(f"\n--- {user_type.upper()} EXPLANATION ---")
        explanation = service.generate_explanation(test_alert, user_type)
        print(json.dumps(explanation, indent=2))


if __name__ == "__main__":
    main()
