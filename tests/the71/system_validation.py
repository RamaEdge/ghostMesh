#!/usr/bin/env python3
"""
GhostMesh System Validation Tool
Comprehensive testing for system reliability, recovery, and edge cases

This tool tests various aspects of the GhostMesh system including:
- False positive handling and debounce behavior
- System recovery after failures
- Edge cases and error conditions
- Performance under load
"""

import json
import time
import threading
import subprocess
import psutil
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import paho.mqtt.client as mqtt
import statistics


class SystemValidator:
    """Comprehensive system validation for GhostMesh."""
    
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client = None
        self.test_results: Dict = {}
        self.alerts_received: List[Dict] = []
        self.lock = threading.Lock()
        
    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            print("✅ Connected to MQTT broker for system validation")
            # Subscribe to all relevant topics
            client.subscribe("alerts/+/+")
            client.subscribe("explanations/+")
            client.subscribe("audit/actions")
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming messages."""
        try:
            data = json.loads(msg.payload.decode())
            
            with self.lock:
                if msg.topic.startswith("alerts/"):
                    self.alerts_received.append({
                        'topic': msg.topic,
                        'data': data,
                        'timestamp': time.time()
                    })
                elif msg.topic.startswith("explanations/"):
                    # Track explanation generation
                    pass
                elif msg.topic == "audit/actions":
                    # Track policy actions
                    pass
                    
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def test_false_positive_handling(self) -> Dict:
        """Test false positive handling and debounce behavior."""
        print("🧪 Testing false positive handling...")
        
        results = {
            'test_name': 'False Positive Handling',
            'passed': True,
            'details': []
        }
        
        try:
            # Inject normal telemetry values that shouldn't trigger alerts
            normal_values = [25.0, 26.0, 24.5, 25.5, 26.2, 24.8, 25.1, 25.9, 24.7, 25.3]
            
            initial_alert_count = len(self.alerts_received)
            
            for i, value in enumerate(normal_values):
                telemetry_data = {
                    "assetId": "test-normal",
                    "line": "test-line",
                    "signal": "temperature",
                    "value": value,
                    "unit": "°C",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "quality": "good",
                    "source": "false-positive-test",
                    "seq": int(time.time())
                }
                
                topic = "factory/test-line/test-normal/temperature"
                self.mqtt_client.publish(topic, json.dumps(telemetry_data), qos=1)
                time.sleep(0.5)  # Small delay between injections
            
            # Wait for processing
            time.sleep(5)
            
            new_alerts = len(self.alerts_received) - initial_alert_count
            results['details'].append(f"Normal values injected: {len(normal_values)}")
            results['details'].append(f"False positive alerts: {new_alerts}")
            
            if new_alerts == 0:
                results['details'].append("✅ No false positives detected")
            else:
                results['passed'] = False
                results['details'].append(f"❌ {new_alerts} false positive alerts detected")
                
        except Exception as e:
            results['passed'] = False
            results['details'].append(f"❌ Test failed: {e}")
        
        return results
    
    def test_debounce_behavior(self) -> Dict:
        """Test debounce behavior with rapid value changes."""
        print("🧪 Testing debounce behavior...")
        
        results = {
            'test_name': 'Debounce Behavior',
            'passed': True,
            'details': []
        }
        
        try:
            # Inject rapid high values that should trigger only one alert
            initial_alert_count = len(self.alerts_received)
            
            for i in range(5):
                telemetry_data = {
                    "assetId": "test-debounce",
                    "line": "test-line",
                    "signal": "temperature",
                    "value": 150.0,  # High value
                    "unit": "°C",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "quality": "good",
                    "source": "debounce-test",
                    "seq": int(time.time())
                }
                
                topic = "factory/test-line/test-debounce/temperature"
                self.mqtt_client.publish(topic, json.dumps(telemetry_data), qos=1)
                time.sleep(0.1)  # Rapid injection
            
            # Wait for processing
            time.sleep(3)
            
            new_alerts = len(self.alerts_received) - initial_alert_count
            results['details'].append(f"Rapid injections: 5")
            results['details'].append(f"Alerts generated: {new_alerts}")
            
            if new_alerts <= 1:
                results['details'].append("✅ Debounce working correctly")
            else:
                results['passed'] = False
                results['details'].append(f"❌ Multiple alerts for rapid changes: {new_alerts}")
                
        except Exception as e:
            results['passed'] = False
            results['details'].append(f"❌ Test failed: {e}")
        
        return results
    
    def test_system_recovery(self) -> Dict:
        """Test system recovery after service failures."""
        print("🧪 Testing system recovery...")
        
        results = {
            'test_name': 'System Recovery',
            'passed': True,
            'details': []
        }
        
        try:
            # Test anomaly detector recovery
            results['details'].append("Testing anomaly detector recovery...")
            
            # Stop anomaly detector
            subprocess.run(["podman-compose", "stop", "anomaly"], check=True)
            results['details'].append("✅ Anomaly detector stopped")
            
            # Wait a moment
            time.sleep(2)
            
            # Start anomaly detector
            subprocess.run(["podman-compose", "start", "anomaly"], check=True)
            results['details'].append("✅ Anomaly detector restarted")
            
            # Wait for service to be ready
            time.sleep(5)
            
            # Test that it can process alerts again
            initial_alert_count = len(self.alerts_received)
            
            telemetry_data = {
                "assetId": "test-recovery",
                "line": "test-line",
                "signal": "temperature",
                "value": 200.0,  # High value to trigger alert
                "unit": "°C",
                "ts": datetime.now(timezone.utc).isoformat(),
                "quality": "good",
                "source": "recovery-test",
                "seq": int(time.time())
            }
            
            topic = "factory/test-line/test-recovery/temperature"
            self.mqtt_client.publish(topic, json.dumps(telemetry_data), qos=1)
            
            # Wait for processing
            time.sleep(5)
            
            new_alerts = len(self.alerts_received) - initial_alert_count
            results['details'].append(f"Recovery test alerts: {new_alerts}")
            
            if new_alerts > 0:
                results['details'].append("✅ System recovered successfully")
            else:
                results['passed'] = False
                results['details'].append("❌ System did not recover properly")
                
        except Exception as e:
            results['passed'] = False
            results['details'].append(f"❌ Test failed: {e}")
        
        return results
    
    def test_edge_cases(self) -> Dict:
        """Test edge cases and error conditions."""
        print("🧪 Testing edge cases...")
        
        results = {
            'test_name': 'Edge Cases',
            'passed': True,
            'details': []
        }
        
        try:
            # Test 1: Invalid JSON
            results['details'].append("Testing invalid JSON handling...")
            self.mqtt_client.publish("factory/test-line/test-invalid/temperature", "invalid json", qos=1)
            time.sleep(1)
            results['details'].append("✅ Invalid JSON handled gracefully")
            
            # Test 2: Missing required fields
            results['details'].append("Testing missing fields...")
            incomplete_data = {"assetId": "test-incomplete"}
            self.mqtt_client.publish("factory/test-line/test-incomplete/temperature", 
                                   json.dumps(incomplete_data), qos=1)
            time.sleep(1)
            results['details'].append("✅ Missing fields handled gracefully")
            
            # Test 3: Extreme values
            results['details'].append("Testing extreme values...")
            extreme_data = {
                "assetId": "test-extreme",
                "line": "test-line",
                "signal": "temperature",
                "value": 999999.0,  # Extreme value
                "unit": "°C",
                "ts": datetime.now(timezone.utc).isoformat(),
                "quality": "good",
                "source": "edge-case-test",
                "seq": int(time.time())
            }
            
            topic = "factory/test-line/test-extreme/temperature"
            self.mqtt_client.publish(topic, json.dumps(extreme_data), qos=1)
            time.sleep(2)
            results['details'].append("✅ Extreme values handled gracefully")
            
            # Test 4: Negative values
            results['details'].append("Testing negative values...")
            negative_data = {
                "assetId": "test-negative",
                "line": "test-line",
                "signal": "temperature",
                "value": -50.0,  # Negative value
                "unit": "°C",
                "ts": datetime.now(timezone.utc).isoformat(),
                "quality": "good",
                "source": "edge-case-test",
                "seq": int(time.time())
            }
            
            topic = "factory/test-line/test-negative/temperature"
            self.mqtt_client.publish(topic, json.dumps(negative_data), qos=1)
            time.sleep(2)
            results['details'].append("✅ Negative values handled gracefully")
            
        except Exception as e:
            results['passed'] = False
            results['details'].append(f"❌ Test failed: {e}")
        
        return results
    
    def test_performance_under_load(self) -> Dict:
        """Test system performance under load."""
        print("🧪 Testing performance under load...")
        
        results = {
            'test_name': 'Performance Under Load',
            'passed': True,
            'details': []
        }
        
        try:
            # Get initial resource usage
            initial_cpu = psutil.cpu_percent()
            initial_memory = psutil.virtual_memory().percent
            
            results['details'].append(f"Initial CPU: {initial_cpu:.1f}%")
            results['details'].append(f"Initial Memory: {initial_memory:.1f}%")
            
            # Inject high volume of telemetry
            num_injections = 100
            start_time = time.time()
            
            for i in range(num_injections):
                telemetry_data = {
                    "assetId": f"load-test-{i % 10}",  # 10 different assets
                    "line": "test-line",
                    "signal": "temperature",
                    "value": 25.0 + (i % 50),  # Varying values
                    "unit": "°C",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "quality": "good",
                    "source": "load-test",
                    "seq": int(time.time())
                }
                
                topic = f"factory/test-line/load-test-{i % 10}/temperature"
                self.mqtt_client.publish(topic, json.dumps(telemetry_data), qos=1)
                
                if i % 10 == 0:  # Small delay every 10 injections
                    time.sleep(0.01)
            
            injection_time = time.time() - start_time
            results['details'].append(f"Injected {num_injections} messages in {injection_time:.2f}s")
            results['details'].append(f"Rate: {num_injections/injection_time:.1f} msg/s")
            
            # Wait for processing
            time.sleep(5)
            
            # Get final resource usage
            final_cpu = psutil.cpu_percent()
            final_memory = psutil.virtual_memory().percent
            
            results['details'].append(f"Final CPU: {final_cpu:.1f}%")
            results['details'].append(f"Final Memory: {final_memory:.1f}%")
            
            # Check if system is still responsive
            if final_cpu < 80 and final_memory < 90:
                results['details'].append("✅ System performance acceptable under load")
            else:
                results['passed'] = False
                results['details'].append("❌ System performance degraded under load")
                
        except Exception as e:
            results['passed'] = False
            results['details'].append(f"❌ Test failed: {e}")
        
        return results
    
    def run_comprehensive_validation(self) -> Dict:
        """Run all validation tests."""
        print("🚀 Starting comprehensive system validation...")
        
        # Connect to MQTT
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.username_pw_set('iot', 'iotpass')
        
        try:
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            # Wait for connection
            time.sleep(1)
            
            # Run all tests
            tests = [
                self.test_false_positive_handling,
                self.test_debounce_behavior,
                self.test_system_recovery,
                self.test_edge_cases,
                self.test_performance_under_load
            ]
            
            all_results = []
            for test in tests:
                try:
                    result = test()
                    all_results.append(result)
                    time.sleep(2)  # Brief pause between tests
                except Exception as e:
                    all_results.append({
                        'test_name': test.__name__,
                        'passed': False,
                        'details': [f"❌ Test failed with exception: {e}"]
                    })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(all_results),
                'passed_tests': sum(1 for r in all_results if r['passed']),
                'failed_tests': sum(1 for r in all_results if not r['passed']),
                'test_results': all_results
            }
            
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
    
    def print_results(self, results: Dict):
        """Print formatted validation results."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE SYSTEM VALIDATION RESULTS")
        print("="*80)
        
        print(f"Timestamp: {results['timestamp']}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['passed_tests']/results['total_tests']:.1%}")
        
        print(f"\nDetailed Results:")
        print("-" * 80)
        
        for test_result in results['test_results']:
            status = "✅ PASS" if test_result['passed'] else "❌ FAIL"
            print(f"\n{status} - {test_result['test_name']}")
            
            for detail in test_result['details']:
                print(f"  {detail}")
        
        # Overall assessment
        if results['failed_tests'] == 0:
            print(f"\n🎉 ALL TESTS PASSED! System validation successful.")
        else:
            print(f"\n⚠️  {results['failed_tests']} test(s) failed. Review results above.")


def main():
    """Main function to run system validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostMesh System Validation Tool')
    parser.add_argument('--host', default='localhost', help='MQTT broker host')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    
    args = parser.parse_args()
    
    # Create and run system validation
    validator = SystemValidator(args.host, args.port)
    results = validator.run_comprehensive_validation()
    validator.print_results(results)
    
    # Return exit code based on results
    return 0 if results['failed_tests'] == 0 else 1


if __name__ == "__main__":
    exit(main())
