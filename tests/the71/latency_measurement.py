#!/usr/bin/env python3
"""
GhostMesh Latency Measurement Tool
Measures end-to-end alert latency from telemetry injection to alert generation

This tool measures the time from when telemetry data is published to MQTT
until the corresponding alert is generated and published.
"""

import json
import time
import threading
import statistics
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import paho.mqtt.client as mqtt
import numpy as np


class LatencyMeasurement:
    """Measures alert latency in the GhostMesh system."""
    
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client = None
        self.measurements: List[Dict] = []
        self.running = False
        self.lock = threading.Lock()
        
    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            print("✅ Connected to MQTT broker for latency measurement")
            # Subscribe to alerts to measure when they're generated
            client.subscribe("alerts/+/+")
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming alert messages."""
        try:
            alert_data = json.loads(msg.payload.decode())
            alert_id = alert_data.get('alertId', 'unknown')
            
            # Check if this is one of our test alerts
            with self.lock:
                for measurement in self.measurements:
                    if measurement['alert_id'] == alert_id and measurement['alert_time'] is None:
                        measurement['alert_time'] = time.time()
                        measurement['latency'] = measurement['alert_time'] - measurement['telemetry_time']
                        print(f"📊 Alert {alert_id}: {measurement['latency']:.3f}s latency")
                        break
                        
        except Exception as e:
            print(f"❌ Error processing alert message: {e}")
    
    def inject_test_telemetry(self, asset_id: str, signal: str, value: float, 
                            expected_alert: bool = True) -> str:
        """Inject test telemetry data and return alert ID for tracking."""
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            raise Exception("MQTT client not connected")
        
        # Generate unique alert ID for tracking
        alert_id = f"latency-test-{int(time.time() * 1000)}"
        
        # Create telemetry data
        telemetry_data = {
            "assetId": asset_id,
            "line": "test-line",
            "signal": signal,
            "value": value,
            "unit": "°C" if signal.lower() in ['temperature', 'temp'] else "bar",
            "ts": datetime.now(timezone.utc).isoformat(),
            "quality": "good",
            "source": "latency-test",
            "seq": int(time.time())
        }
        
        # Record telemetry injection time
        telemetry_time = time.time()
        
        # Publish telemetry
        topic = f"factory/test-line/{asset_id}/{signal}"
        self.mqtt_client.publish(topic, json.dumps(telemetry_data), qos=1)
        
        # Create measurement record
        measurement = {
            'alert_id': alert_id,
            'asset_id': asset_id,
            'signal': signal,
            'value': value,
            'telemetry_time': telemetry_time,
            'alert_time': None,
            'latency': None,
            'expected_alert': expected_alert
        }
        
        with self.lock:
            self.measurements.append(measurement)
        
        print(f"📤 Injected telemetry: {asset_id}/{signal} = {value}")
        return alert_id
    
    def run_latency_test(self, num_tests: int = 10, delay: float = 2.0) -> Dict:
        """Run comprehensive latency tests."""
        print(f"🚀 Starting latency test with {num_tests} measurements...")
        
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
            
            # Run tests
            for i in range(num_tests):
                # Inject high-value telemetry that should trigger alerts
                asset_id = f"test-asset-{i % 3 + 1}"  # Rotate between 3 assets
                signal = "temperature"
                value = 120.0 + (i * 5)  # High values to trigger alerts
                
                self.inject_test_telemetry(asset_id, signal, value)
                
                if i < num_tests - 1:  # Don't delay after last test
                    time.sleep(delay)
            
            # Wait for all alerts to be processed
            print("⏳ Waiting for alerts to be processed...")
            max_wait = 30  # Maximum wait time in seconds
            start_wait = time.time()
            
            while time.time() - start_wait < max_wait:
                with self.lock:
                    completed = sum(1 for m in self.measurements if m['latency'] is not None)
                    if completed >= num_tests:
                        break
                time.sleep(0.5)
            
            # Calculate statistics
            return self.calculate_statistics()
            
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
    
    def calculate_statistics(self) -> Dict:
        """Calculate latency statistics from measurements."""
        with self.lock:
            latencies = [m['latency'] for m in self.measurements if m['latency'] is not None]
            total_measurements = len(self.measurements)
            completed_measurements = len(latencies)
            
            if not latencies:
                return {
                    'total_measurements': total_measurements,
                    'completed_measurements': 0,
                    'success_rate': 0.0,
                    'avg_latency': None,
                    'min_latency': None,
                    'max_latency': None,
                    'median_latency': None,
                    'p95_latency': None,
                    'p99_latency': None,
                    'under_2s_rate': 0.0
                }
            
            stats = {
                'total_measurements': total_measurements,
                'completed_measurements': completed_measurements,
                'success_rate': completed_measurements / total_measurements,
                'avg_latency': statistics.mean(latencies),
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'median_latency': statistics.median(latencies),
                'p95_latency': np.percentile(latencies, 95),
                'p99_latency': np.percentile(latencies, 99),
                'under_2s_rate': sum(1 for l in latencies if l <= 2.0) / len(latencies)
            }
            
            return stats
    
    def print_results(self, stats: Dict):
        """Print formatted test results."""
        print("\n" + "="*60)
        print("📊 LATENCY MEASUREMENT RESULTS")
        print("="*60)
        
        print(f"Total Measurements: {stats['total_measurements']}")
        print(f"Completed Measurements: {stats['completed_measurements']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        
        if stats['avg_latency'] is not None:
            print(f"\nLatency Statistics:")
            print(f"  Average: {stats['avg_latency']:.3f}s")
            print(f"  Median:  {stats['median_latency']:.3f}s")
            print(f"  Min:     {stats['min_latency']:.3f}s")
            print(f"  Max:     {stats['max_latency']:.3f}s")
            print(f"  95th %:  {stats['p95_latency']:.3f}s")
            print(f"  99th %:  {stats['p99_latency']:.3f}s")
            
            print(f"\nTarget Performance:")
            print(f"  Under 2s: {stats['under_2s_rate']:.1%}")
            
            # Performance assessment
            if stats['avg_latency'] <= 2.0 and stats['under_2s_rate'] >= 0.95:
                print(f"\n✅ PASS: Latency targets met!")
            elif stats['avg_latency'] <= 2.0:
                print(f"\n⚠️  WARNING: Average latency OK, but some outliers >2s")
            else:
                print(f"\n❌ FAIL: Average latency exceeds 2s target")
        else:
            print(f"\n❌ No successful measurements recorded")


def main():
    """Main function to run latency measurements."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostMesh Latency Measurement Tool')
    parser.add_argument('--host', default='localhost', help='MQTT broker host')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--tests', type=int, default=10, help='Number of test measurements')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between tests (seconds)')
    
    args = parser.parse_args()
    
    # Create and run latency measurement
    measurer = LatencyMeasurement(args.host, args.port)
    stats = measurer.run_latency_test(args.tests, args.delay)
    measurer.print_results(stats)
    
    # Return exit code based on results
    if stats['avg_latency'] is not None and stats['avg_latency'] <= 2.0 and stats['under_2s_rate'] >= 0.95:
        return 0  # Success
    else:
        return 1  # Failure


if __name__ == "__main__":
    exit(main())
