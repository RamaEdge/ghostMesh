#!/usr/bin/env python3
"""
GhostMesh Runtime Validation Script

This script validates the GhostMesh system at runtime.
It checks service health, data flow, performance metrics, and system status.

Usage:
    python3 scripts/validate-runtime.py [--verbose] [--timeout 30]
"""

import argparse
import json
import os
import subprocess
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class RuntimeValidationError(Exception):
    """Custom exception for runtime validation errors."""
    pass


class GhostMeshRuntimeValidator:
    """GhostMesh runtime validator."""
    
    def __init__(self, verbose: bool = False, timeout: int = 30):
        self.verbose = verbose
        self.timeout = timeout
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, any] = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with appropriate level."""
        if level == "ERROR":
            self.errors.append(message)
            print(f"❌ ERROR: {message}")
        elif level == "WARNING":
            self.warnings.append(message)
            print(f"⚠️  WARNING: {message}")
        elif self.verbose or level == "INFO":
            print(f"ℹ️  {message}")
    
    def run_command(self, command: str, check: bool = True) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=check, timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {self.timeout} seconds"
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
    
    def check_service_status(self) -> bool:
        """Check if all services are running."""
        self.log("Checking service status...")
        
        exit_code, stdout, stderr = self.run_command("docker-compose ps", check=False)
        if exit_code != 0:
            self.log("Failed to get service status", "ERROR")
            return False
        
        lines = stdout.strip().split('\n')
        running_services = []
        stopped_services = []
        
        for line in lines:
            if 'ghostmesh-' in line:
                if 'Up' in line:
                    running_services.append(line.split()[0])
                else:
                    stopped_services.append(line.split()[0])
        
        self.log(f"Running services: {len(running_services)}")
        for service in running_services:
            self.log(f"  ✓ {service}")
        
        if stopped_services:
            self.log(f"Stopped services: {len(stopped_services)}", "WARNING")
            for service in stopped_services:
                self.log(f"  ❌ {service}", "WARNING")
        
        self.metrics['running_services'] = len(running_services)
        self.metrics['total_services'] = len(running_services) + len(stopped_services)
        
        return len(stopped_services) == 0
    
    def check_mqtt_connectivity(self) -> bool:
        """Check MQTT broker connectivity."""
        self.log("Checking MQTT broker connectivity...")
        
        # Test MQTT connection
        test_command = (
            "docker exec ghostmesh-mosquitto mosquitto_pub "
            "-h localhost -t test/connectivity -m 'test' "
            "-u iot -P iotpass"
        )
        
        exit_code, stdout, stderr = self.run_command(test_command, check=False)
        if exit_code != 0:
            self.log(f"MQTT connectivity test failed: {stderr}", "ERROR")
            return False
        
        self.log("✓ MQTT broker is accessible")
        return True
    
    def check_llm_server_health(self) -> bool:
        """Check LLM server health."""
        self.log("Checking LLM server health...")
        
        try:
            response = requests.get("http://localhost:8080/health", timeout=10)
            if response.status_code == 200:
                self.log("✓ LLM server is healthy")
                return True
            else:
                self.log(f"LLM server health check failed: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"LLM server health check failed: {e}", "ERROR")
            return False
    
    def check_dashboard_health(self) -> bool:
        """Check dashboard health."""
        self.log("Checking dashboard health...")
        
        try:
            response = requests.get("http://localhost:8501/health", timeout=10)
            if response.status_code == 200:
                self.log("✓ Dashboard is healthy")
                return True
            else:
                self.log(f"Dashboard health check failed: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Dashboard health check failed: {e}", "ERROR")
            return False
    
    def check_data_flow(self) -> bool:
        """Check if data is flowing through the system."""
        self.log("Checking data flow...")
        
        # Check for telemetry data
        telemetry_command = (
            "docker exec ghostmesh-mosquitto mosquitto_sub "
            "-h localhost -u gateway -P gatewaypass "
            "-t 'factory/+/+/+' -C 5 -W 5"
        )
        
        exit_code, stdout, stderr = self.run_command(telemetry_command, check=False)
        if exit_code != 0:
            self.log(f"Failed to check telemetry data: {stderr}", "ERROR")
            return False
        
        if not stdout.strip():
            self.log("No telemetry data detected", "WARNING")
            return True  # Not critical, might be normal
        
        # Count telemetry messages
        telemetry_count = len([line for line in stdout.strip().split('\n') if line.strip()])
        self.log(f"✓ Detected {telemetry_count} telemetry messages")
        self.metrics['telemetry_messages'] = telemetry_count
        
        return True
    
    def check_anomaly_detection(self) -> bool:
        """Check if anomaly detection is working."""
        self.log("Checking anomaly detection...")
        
        # Check for alert data
        alert_command = (
            "docker exec ghostmesh-mosquitto mosquitto_sub "
            "-h localhost -u iot -P iotpass "
            "-t 'alerts/+/+' -C 5 -W 5"
        )
        
        exit_code, stdout, stderr = self.run_command(alert_command, check=False)
        if exit_code != 0:
            self.log(f"Failed to check alert data: {stderr}", "ERROR")
            return False
        
        if not stdout.strip():
            self.log("No alerts detected (this may be normal)", "INFO")
            return True  # Not critical, no anomalies detected
        
        # Count alert messages
        alert_count = len([line for line in stdout.strip().split('\n') if line.strip()])
        self.log(f"✓ Detected {alert_count} alert messages")
        self.metrics['alert_messages'] = alert_count
        
        return True
    
    def check_explanations(self) -> bool:
        """Check if explanations are being generated."""
        self.log("Checking explanation generation...")
        
        # Check for explanation data
        explanation_command = (
            "docker exec ghostmesh-mosquitto mosquitto_sub "
            "-h localhost -u explainer -P explainerpass "
            "-t 'explanations/+' -C 5 -W 5"
        )
        
        exit_code, stdout, stderr = self.run_command(explanation_command, check=False)
        if exit_code != 0:
            self.log(f"Failed to check explanation data: {stderr}", "ERROR")
            return False
        
        if not stdout.strip():
            self.log("No explanations detected (this may be normal)", "INFO")
            return True  # Not critical, no explanations generated
        
        # Count explanation messages
        explanation_count = len([line for line in stdout.strip().split('\n') if line.strip()])
        self.log(f"✓ Detected {explanation_count} explanation messages")
        self.metrics['explanation_messages'] = explanation_count
        
        return True
    
    def check_resource_usage(self) -> bool:
        """Check system resource usage."""
        self.log("Checking resource usage...")
        
        # Check container resource usage
        exit_code, stdout, stderr = self.run_command("docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'", check=False)
        if exit_code != 0:
            self.log(f"Failed to get resource usage: {stderr}", "WARNING")
            return True  # Not critical
        
        lines = stdout.strip().split('\n')
        high_cpu_services = []
        high_memory_services = []
        
        for line in lines[1:]:  # Skip header
            if 'ghostmesh-' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    container = parts[0]
                    cpu_percent = parts[1].replace('%', '')
                    memory_usage = parts[2]
                    
                    try:
                        cpu_float = float(cpu_percent)
                        if cpu_float > 80:
                            high_cpu_services.append(f"{container} ({cpu_percent}%)")
                    except ValueError:
                        pass
        
        if high_cpu_services:
            self.log(f"High CPU usage detected: {', '.join(high_cpu_services)}", "WARNING")
        
        self.log("✓ Resource usage check completed")
        return True
    
    def check_log_errors(self) -> bool:
        """Check for errors in service logs."""
        self.log("Checking for log errors...")
        
        services = [
            "ghostmesh-mosquitto",
            "ghostmesh-gateway", 
            "ghostmesh-detector",
            "ghostmesh-explainer",
            "ghostmesh-llm-server",
            "ghostmesh-dashboard",
            "ghostmesh-policy"
        ]
        
        error_count = 0
        for service in services:
            # Check for ERROR level logs in the last 100 lines
            log_command = f"docker logs --tail 100 {service} 2>&1 | grep -i error | wc -l"
            exit_code, stdout, stderr = self.run_command(log_command, check=False)
            
            if exit_code == 0:
                try:
                    errors = int(stdout.strip())
                    if errors > 0:
                        self.log(f"Found {errors} errors in {service} logs", "WARNING")
                        error_count += errors
                except ValueError:
                    pass
        
        if error_count == 0:
            self.log("✓ No recent errors found in service logs")
        else:
            self.log(f"Total errors found: {error_count}", "WARNING")
        
        self.metrics['log_errors'] = error_count
        return True
    
    def run_validation(self) -> bool:
        """Run all runtime validation checks."""
        self.log("Starting GhostMesh runtime validation...")
        self.log("=" * 50)
        
        checks = [
            ("Service Status", self.check_service_status),
            ("MQTT Connectivity", self.check_mqtt_connectivity),
            ("LLM Server Health", self.check_llm_server_health),
            ("Dashboard Health", self.check_dashboard_health),
            ("Data Flow", self.check_data_flow),
            ("Anomaly Detection", self.check_anomaly_detection),
            ("Explanations", self.check_explanations),
            ("Resource Usage", self.check_resource_usage),
            ("Log Errors", self.check_log_errors),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            self.log(f"\n--- {check_name} ---")
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                self.log(f"Check failed with exception: {e}", "ERROR")
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """Print validation summary."""
        self.log("\n" + "=" * 50)
        self.log("RUNTIME VALIDATION SUMMARY")
        self.log("=" * 50)
        
        # Print metrics
        if self.metrics:
            self.log("\n📊 Metrics:")
            for key, value in self.metrics.items():
                self.log(f"  - {key}: {value}")
        
        if self.warnings:
            self.log(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                self.log(f"  - {warning}")
        
        if self.errors:
            self.log(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                self.log(f"  - {error}")
        
        if not self.errors:
            self.log("\n✅ All runtime validation checks passed!")
            self.log("GhostMesh is running correctly.")
        else:
            self.log(f"\n❌ Runtime validation failed with {len(self.errors)} errors.")
            self.log("Please check the errors above.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate GhostMesh runtime")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout for checks in seconds")
    
    args = parser.parse_args()
    
    validator = GhostMeshRuntimeValidator(verbose=args.verbose, timeout=args.timeout)
    
    try:
        success = validator.run_validation()
        validator.print_summary()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nRuntime validation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nRuntime validation failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
