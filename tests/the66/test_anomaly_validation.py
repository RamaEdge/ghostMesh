#!/usr/bin/env python3
"""
THE-66: Anomaly Injection and Alert Validation Testing

This module implements comprehensive tests for anomaly injection and alert validation
according to THE-66 requirements:

- Induce synthetic anomalies (spike, flood, drift)
- Verify alert generation within 2-second latency requirement
- Test isolate/unblock functionality
- Validate alert severity classification
- Test debounce behavior and false positive handling
"""

import json
import time
import subprocess
import sys
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt

# Import our anomaly injector
from anomaly_injector import AnomalyInjector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnomalyValidationTester:
    """Comprehensive tester for anomaly injection and alert validation."""
    
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883):
        """Initialize the validation tester."""
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        
        # Test results tracking
        self.test_results = {
            "anomaly_injection": {"passed": 0, "failed": 0, "details": []},
            "latency_validation": {"passed": 0, "failed": 0, "details": []},
            "policy_enforcement": {"passed": 0, "failed": 0, "details": []},
            "severity_classification": {"passed": 0, "failed": 0, "details": []},
            "debounce_behavior": {"passed": 0, "failed": 0, "details": []}
        }
        
        # MQTT client for monitoring
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        
        # Alert monitoring
        self.received_alerts = []
        self.policy_actions = []
        
        # Anomaly injector
        self.injector = AnomalyInjector(mqtt_host, mqtt_port)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            logger.info("Validation tester connected to MQTT broker")
            # Subscribe to alerts and policy actions
            client.subscribe("alerts/+/+")
            client.subscribe("audit/actions")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, message):
        """Handle received MQTT messages."""
        try:
            data = json.loads(message.payload.decode())
            
            if message.topic.startswith("alerts/"):
                self.received_alerts.append({
                    "topic": message.topic,
                    "data": data,
                    "timestamp": time.time()
                })
                logger.info(f"Received alert: {data.get('assetId')}/{data.get('signal')} - {data.get('severity')}")
            
            elif message.topic == "audit/actions":
                self.policy_actions.append({
                    "data": data,
                    "timestamp": time.time()
                })
                logger.info(f"Received policy action: {data.get('action')} on {data.get('assetId')}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            time.sleep(1)
            
            if not self.injector.connect():
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.injector.disconnect()
    
    def test_anomaly_injection(self) -> bool:
        """Test that anomalies can be injected reliably."""
        logger.info("=== Testing Anomaly Injection ===")
        
        test_cases = [
            {"type": "spike", "asset": "press01", "signal": "temperature", "multiplier": 3.0},
            {"type": "flood", "asset": "press02", "signal": "pressure", "count": 8},
            {"type": "drift", "asset": "conveyor01", "signal": "speed", "rate": 0.15}
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Test case {i+1}: {test_case['type']} anomaly on {test_case['asset']}/{test_case['signal']}")
            
            try:
                if test_case["type"] == "spike":
                    alert_id = self.injector.inject_spike_anomaly(
                        test_case["asset"], test_case["signal"], 
                        spike_multiplier=test_case["multiplier"]
                    )
                elif test_case["type"] == "flood":
                    alert_id = self.injector.inject_flood_anomaly(
                        test_case["asset"], test_case["signal"],
                        flood_count=test_case["count"]
                    )
                elif test_case["type"] == "drift":
                    alert_id = self.injector.inject_drift_anomaly(
                        test_case["asset"], test_case["signal"],
                        drift_rate=test_case["rate"], duration_seconds=15
                    )
                
                # Wait for injection to complete
                time.sleep(10)
                
                self.test_results["anomaly_injection"]["passed"] += 1
                self.test_results["anomaly_injection"]["details"].append({
                    "test_case": test_case,
                    "alert_id": alert_id,
                    "status": "PASSED"
                })
                logger.info(f"✓ {test_case['type']} injection successful")
                
            except Exception as e:
                all_passed = False
                self.test_results["anomaly_injection"]["failed"] += 1
                self.test_results["anomaly_injection"]["details"].append({
                    "test_case": test_case,
                    "error": str(e),
                    "status": "FAILED"
                })
                logger.error(f"✗ {test_case['type']} injection failed: {e}")
        
        return all_passed
    
    def test_latency_validation(self) -> bool:
        """Test that alerts are generated within 2-second latency requirement."""
        logger.info("=== Testing Alert Latency Validation ===")
        
        # Clear previous measurements
        self.injector.clear_measurements()
        
        # Inject multiple anomalies and measure latency
        test_anomalies = [
            ("press01", "temperature", "spike"),
            ("press02", "pressure", "flood"),
            ("conveyor01", "speed", "drift")
        ]
        
        for asset, signal, anomaly_type in test_anomalies:
            logger.info(f"Injecting {anomaly_type} anomaly on {asset}/{signal}")
            
            if anomaly_type == "spike":
                self.injector.inject_spike_anomaly(asset, signal, spike_multiplier=3.0)
            elif anomaly_type == "flood":
                self.injector.inject_flood_anomaly(asset, signal, flood_count=8)
            elif anomaly_type == "drift":
                self.injector.inject_drift_anomaly(asset, signal, drift_rate=0.15, duration_seconds=10)
            
            time.sleep(8)  # Wait for detection
        
        # Get latency statistics
        stats = self.injector.get_latency_statistics()
        logger.info(f"Latency Statistics: {stats}")
        
        # Validate latency requirements
        all_passed = True
        max_allowed_latency = 2.0  # 2-second requirement
        
        if stats["count"] > 0:
            if stats["max_latency"] <= max_allowed_latency:
                self.test_results["latency_validation"]["passed"] += 1
                self.test_results["latency_validation"]["details"].append({
                    "max_latency": stats["max_latency"],
                    "avg_latency": stats["avg_latency"],
                    "count": stats["count"],
                    "status": "PASSED"
                })
                logger.info(f"✓ Latency validation passed: max={stats['max_latency']:.3f}s")
            else:
                all_passed = False
                self.test_results["latency_validation"]["failed"] += 1
                self.test_results["latency_validation"]["details"].append({
                    "max_latency": stats["max_latency"],
                    "avg_latency": stats["avg_latency"],
                    "count": stats["count"],
                    "status": "FAILED",
                    "reason": f"Max latency {stats['max_latency']:.3f}s exceeds 2s requirement"
                })
                logger.error(f"✗ Latency validation failed: max={stats['max_latency']:.3f}s > 2s")
        else:
            all_passed = False
            self.test_results["latency_validation"]["failed"] += 1
            self.test_results["latency_validation"]["details"].append({
                "status": "FAILED",
                "reason": "No latency measurements recorded"
            })
            logger.error("✗ No latency measurements recorded")
        
        return all_passed
    
    def test_policy_enforcement(self) -> bool:
        """Test isolate/unblock functionality."""
        logger.info("=== Testing Policy Enforcement ===")
        
        # Clear previous policy actions
        self.policy_actions.clear()
        
        # Test isolate action
        logger.info("Testing isolate action...")
        isolate_command = {
            "action": "isolate",
            "assetId": "press01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "THE-66 test"
        }
        
        self.mqtt_client.publish("control/press01/isolate", json.dumps(isolate_command), qos=1)
        time.sleep(3)  # Wait for policy action
        
        # Check if isolate action was received
        isolate_received = any(
            action["data"].get("action") == "isolate" and 
            action["data"].get("assetId") == "press01"
            for action in self.policy_actions
        )
        
        # Test unblock action
        logger.info("Testing unblock action...")
        unblock_command = {
            "action": "unblock",
            "assetId": "press01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "THE-66 test"
        }
        
        self.mqtt_client.publish("control/press01/unblock", json.dumps(unblock_command), qos=1)
        time.sleep(3)  # Wait for policy action
        
        # Check if unblock action was received
        unblock_received = any(
            action["data"].get("action") == "unblock" and 
            action["data"].get("assetId") == "press01"
            for action in self.policy_actions
        )
        
        # Validate results
        all_passed = True
        
        if isolate_received:
            self.test_results["policy_enforcement"]["passed"] += 1
            self.test_results["policy_enforcement"]["details"].append({
                "action": "isolate",
                "status": "PASSED"
            })
            logger.info("✓ Isolate action successful")
        else:
            all_passed = False
            self.test_results["policy_enforcement"]["failed"] += 1
            self.test_results["policy_enforcement"]["details"].append({
                "action": "isolate",
                "status": "FAILED",
                "reason": "Isolate action not received"
            })
            logger.error("✗ Isolate action failed")
        
        if unblock_received:
            self.test_results["policy_enforcement"]["passed"] += 1
            self.test_results["policy_enforcement"]["details"].append({
                "action": "unblock",
                "status": "PASSED"
            })
            logger.info("✓ Unblock action successful")
        else:
            all_passed = False
            self.test_results["policy_enforcement"]["failed"] += 1
            self.test_results["policy_enforcement"]["details"].append({
                "action": "unblock",
                "status": "FAILED",
                "reason": "Unblock action not received"
            })
            logger.error("✗ Unblock action failed")
        
        return all_passed
    
    def test_severity_classification(self) -> bool:
        """Validate alert severity classification."""
        logger.info("=== Testing Alert Severity Classification ===")
        
        # Clear previous alerts
        self.received_alerts.clear()
        
        # Test different severity levels by injecting anomalies with different intensities
        severity_tests = [
            {"asset": "press01", "signal": "temperature", "multiplier": 2.5, "expected_severity": "medium"},
            {"asset": "press02", "signal": "pressure", "multiplier": 4.0, "expected_severity": "high"},
            {"asset": "conveyor01", "signal": "speed", "multiplier": 1.8, "expected_severity": "low"}
        ]
        
        all_passed = True
        
        for test in severity_tests:
            logger.info(f"Testing severity classification: {test['expected_severity']} on {test['asset']}/{test['signal']}")
            
            # Inject anomaly
            self.injector.inject_spike_anomaly(
                test["asset"], test["signal"], 
                spike_multiplier=test["multiplier"]
            )
            
            time.sleep(8)  # Wait for detection
            
            # Check if alert was received with correct severity
            matching_alerts = [
                alert for alert in self.received_alerts
                if (alert["data"].get("assetId") == test["asset"] and 
                    alert["data"].get("signal") == test["signal"])
            ]
            
            if matching_alerts:
                latest_alert = max(matching_alerts, key=lambda x: x["timestamp"])
                actual_severity = latest_alert["data"].get("severity", "unknown")
                
                if actual_severity == test["expected_severity"]:
                    self.test_results["severity_classification"]["passed"] += 1
                    self.test_results["severity_classification"]["details"].append({
                        "test": test,
                        "actual_severity": actual_severity,
                        "status": "PASSED"
                    })
                    logger.info(f"✓ Severity classification correct: {actual_severity}")
                else:
                    all_passed = False
                    self.test_results["severity_classification"]["failed"] += 1
                    self.test_results["severity_classification"]["details"].append({
                        "test": test,
                        "actual_severity": actual_severity,
                        "expected_severity": test["expected_severity"],
                        "status": "FAILED"
                    })
                    logger.error(f"✗ Severity classification incorrect: expected {test['expected_severity']}, got {actual_severity}")
            else:
                all_passed = False
                self.test_results["severity_classification"]["failed"] += 1
                self.test_results["severity_classification"]["details"].append({
                    "test": test,
                    "status": "FAILED",
                    "reason": "No alert received"
                })
                logger.error(f"✗ No alert received for {test['asset']}/{test['signal']}")
        
        return all_passed
    
    def test_debounce_behavior(self) -> bool:
        """Test debounce behavior and false positive handling."""
        logger.info("=== Testing Debounce Behavior ===")
        
        # Clear previous alerts
        self.received_alerts.clear()
        
        # Inject rapid successive anomalies to test debounce
        logger.info("Injecting rapid successive anomalies to test debounce...")
        
        asset = "press01"
        signal = "temperature"
        
        # Inject 5 rapid anomalies within debounce window
        for i in range(5):
            self.injector.inject_spike_anomaly(asset, signal, spike_multiplier=3.0)
            time.sleep(1)  # 1-second intervals (within 30s debounce window)
        
        time.sleep(10)  # Wait for processing
        
        # Count alerts for this asset/signal
        debounce_alerts = [
            alert for alert in self.received_alerts
            if (alert["data"].get("assetId") == asset and 
                alert["data"].get("signal") == signal)
        ]
        
        # Debounce should limit alerts (ideally 1 alert for 5 rapid anomalies)
        alert_count = len(debounce_alerts)
        
        if alert_count <= 2:  # Allow some tolerance
            self.test_results["debounce_behavior"]["passed"] += 1
            self.test_results["debounce_behavior"]["details"].append({
                "anomalies_injected": 5,
                "alerts_received": alert_count,
                "status": "PASSED"
            })
            logger.info(f"✓ Debounce behavior working: {alert_count} alerts for 5 anomalies")
        else:
            self.test_results["debounce_behavior"]["failed"] += 1
            self.test_results["debounce_behavior"]["details"].append({
                "anomalies_injected": 5,
                "alerts_received": alert_count,
                "status": "FAILED",
                "reason": f"Too many alerts ({alert_count}) for debounced anomalies"
            })
            logger.error(f"✗ Debounce behavior failed: {alert_count} alerts for 5 anomalies")
            return False
        
        return True
    
    def run_comprehensive_test(self) -> Dict:
        """Run all THE-66 tests and return results."""
        logger.info("Starting THE-66 Comprehensive Anomaly Validation Test")
        logger.info("=" * 60)
        
        if not self.connect():
            logger.error("Failed to connect to MQTT broker")
            return {"error": "Connection failed"}
        
        try:
            # Run all test categories
            tests = [
                ("Anomaly Injection", self.test_anomaly_injection),
                ("Latency Validation", self.test_latency_validation),
                ("Policy Enforcement", self.test_policy_enforcement),
                ("Severity Classification", self.test_severity_classification),
                ("Debounce Behavior", self.test_debounce_behavior)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\nRunning {test_name} test...")
                try:
                    test_func()
                except Exception as e:
                    logger.error(f"Test {test_name} failed with exception: {e}")
            
            # Generate summary
            total_passed = sum(category["passed"] for category in self.test_results.values())
            total_failed = sum(category["failed"] for category in self.test_results.values())
            
            summary = {
                "test_summary": {
                    "total_passed": total_passed,
                    "total_failed": total_failed,
                    "success_rate": total_passed / (total_passed + total_failed) * 100 if (total_passed + total_failed) > 0 else 0
                },
                "detailed_results": self.test_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("\n" + "=" * 60)
            logger.info("THE-66 Test Results Summary")
            logger.info("=" * 60)
            logger.info(f"Total Tests Passed: {total_passed}")
            logger.info(f"Total Tests Failed: {total_failed}")
            logger.info(f"Success Rate: {summary['test_summary']['success_rate']:.1f}%")
            
            for category, results in self.test_results.items():
                logger.info(f"{category.replace('_', ' ').title()}: {results['passed']} passed, {results['failed']} failed")
            
            return summary
            
        finally:
            self.disconnect()


def main():
    """Main function to run THE-66 tests."""
    tester = AnomalyValidationTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open("tests/the66/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("Test results saved to tests/the66/test_results.json")
    
    # Exit with appropriate code
    if results.get("test_summary", {}).get("total_failed", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
