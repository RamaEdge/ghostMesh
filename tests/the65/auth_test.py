#!/usr/bin/env python3
"""
THE-65 Authentication Test
Verifies MQTT authentication across all GhostMesh services

This script tests:
1. MQTT broker authentication configuration
2. Service authentication with correct credentials
3. Service authentication with incorrect credentials
4. ACL (Access Control List) enforcement
5. Cross-service authentication compatibility
"""

import json
import subprocess
import sys
import time
from typing import Dict, List, Tuple


def run_command(cmd: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a shell command with timeout and return result."""
    print(f"$ {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Command timed out after {timeout}s: {cmd}")
        return subprocess.CompletedProcess(cmd, 1, "", "Timeout")


def test_mqtt_anonymous_access() -> bool:
    """Test if anonymous access is allowed (should be false in production)."""
    print("\n=== Testing Anonymous MQTT Access ===")
    
    # Test anonymous publish
    cmd = "podman exec ghostmesh-mosquitto mosquitto_pub -h localhost -t 'test/anonymous' -m 'test' -q 1"
    result = run_command(cmd, timeout=5)
    
    if result.returncode == 0:
        print("⚠️  WARNING: Anonymous access is ENABLED")
        return True
    else:
        print("✓ Anonymous access is DISABLED (secure)")
        return False


def test_mqtt_authenticated_access(credentials: List[Tuple[str, str]]) -> Dict[str, bool]:
    """Test MQTT access with various credentials."""
    print("\n=== Testing Authenticated MQTT Access ===")
    
    results = {}
    
    for username, password in credentials:
        print(f"\nTesting credentials: {username}:{password}")
        
        # Test publish with credentials
        cmd = f"podman exec ghostmesh-mosquitto mosquitto_pub -h localhost -t 'test/auth/{username}' -m 'test' -u '{username}' -P '{password}' -q 1"
        result = run_command(cmd, timeout=5)
        
        if result.returncode == 0:
            print(f"  ✓ {username}: Authentication SUCCESS")
            results[f"{username}_publish"] = True
        else:
            print(f"  ✗ {username}: Authentication FAILED - {result.stderr}")
            results[f"{username}_publish"] = False
        
        # Test subscribe with credentials
        cmd = f"podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -t 'test/auth/{username}' -C 1 -u '{username}' -P '{password}'"
        result = run_command(cmd, timeout=3)
        
        if result.returncode == 0:
            print(f"  ✓ {username}: Subscribe SUCCESS")
            results[f"{username}_subscribe"] = True
        else:
            print(f"  ✗ {username}: Subscribe FAILED - {result.stderr}")
            results[f"{username}_subscribe"] = False
    
    return results


def test_service_authentication() -> Dict[str, bool]:
    """Test if services are using authentication."""
    print("\n=== Testing Service Authentication ===")
    
    results = {}
    
    # Check if services are running with authentication
    services = [
        ("ghostmesh-gateway", "gateway", "gatewaypass"),
        ("ghostmesh-detector", "iot", "iotpass"),
        ("ghostmesh-policy", "iot", "iotpass"),
        ("ghostmesh-dashboard", "iot", "iotpass")
    ]
    
    for service, username, password in services:
        print(f"\nTesting {service} authentication...")
        
        # Check if service is running
        cmd = f"podman ps --filter name={service} --format '{{{{.Status}}}}'"
        result = run_command(cmd, timeout=5)
        
        if result.returncode == 0 and "Up" in result.stdout:
            print(f"  ✓ {service} is running")
            
            # Test if service can publish to its expected topics
            if service == "ghostmesh-gateway":
                test_topic = "factory/Line1/TestAsset/TestSignal"
            elif service == "ghostmesh-detector":
                test_topic = "alerts/TestAsset/TestSignal"
            elif service == "ghostmesh-policy":
                test_topic = "audit/actions"
            else:  # dashboard
                test_topic = "test/dashboard"
            
            cmd = f"podman exec ghostmesh-mosquitto mosquitto_pub -h localhost -t '{test_topic}' -m '{{}}' -u '{username}' -P '{password}' -q 1"
            result = run_command(cmd, timeout=5)
            
            if result.returncode == 0:
                print(f"  ✓ {service} can publish to MQTT with auth")
                results[f"{service}_auth"] = True
            else:
                print(f"  ✗ {service} cannot publish to MQTT - {result.stderr}")
                results[f"{service}_auth"] = False
        else:
            print(f"  ✗ {service} is not running")
            results[f"{service}_auth"] = False
    
    return results


def test_acl_enforcement() -> Dict[str, bool]:
    """Test Access Control List enforcement."""
    print("\n=== Testing ACL Enforcement ===")
    
    results = {}
    
    # Test different user permissions
    test_cases = [
        ("iot", "iotpass", "factory/Line1/TestAsset/TestSignal", True),  # Should work
        ("iot", "iotpass", "alerts/TestAsset/TestSignal", True),         # Should work
        ("gateway", "gatewaypass", "factory/Line1/TestAsset/TestSignal", True),  # Should work
        ("gateway", "gatewaypass", "alerts/TestAsset/TestSignal", False), # Should fail (no alert access)
        ("invalid", "invalid", "factory/Line1/TestAsset/TestSignal", False), # Should fail
    ]
    
    for username, password, topic, should_succeed in test_cases:
        print(f"\nTesting ACL: {username} -> {topic} (expect: {'SUCCESS' if should_succeed else 'FAIL'})")
        
        cmd = f"podman exec ghostmesh-mosquitto mosquitto_pub -h localhost -t '{topic}' -m 'test' -u '{username}' -P '{password}' -q 1"
        result = run_command(cmd, timeout=5)
        
        if result.returncode == 0 and should_succeed:
            print(f"  ✓ ACL test PASSED: {username} can access {topic}")
            results[f"{username}_{topic.replace('/', '_')}"] = True
        elif result.returncode != 0 and not should_succeed:
            print(f"  ✓ ACL test PASSED: {username} correctly denied access to {topic}")
            results[f"{username}_{topic.replace('/', '_')}"] = True
        else:
            print(f"  ✗ ACL test FAILED: {username} access to {topic} was unexpected")
            results[f"{username}_{topic.replace('/', '_')}"] = False
    
    return results


def check_mosquitto_config() -> Dict[str, str]:
    """Check current Mosquitto configuration."""
    print("\n=== Checking Mosquitto Configuration ===")
    
    config_status = {}
    
    # Check if password file is enabled
    cmd = "podman exec ghostmesh-mosquitto cat /mosquitto/config/mosquitto.conf | grep -E 'password_file|acl_file|allow_anonymous'"
    result = run_command(cmd, timeout=5)
    
    if result.returncode == 0:
        config_lines = result.stdout.strip().split('\n')
        for line in config_lines:
            if 'allow_anonymous' in line:
                config_status['allow_anonymous'] = line.strip()
            elif 'password_file' in line:
                config_status['password_file'] = line.strip()
            elif 'acl_file' in line:
                config_status['acl_file'] = line.strip()
    
    # Check if password file exists and has content
    cmd = "podman exec ghostmesh-mosquitto ls -la /mosquitto/config/passwd"
    result = run_command(cmd, timeout=5)
    
    if result.returncode == 0:
        config_status['passwd_file_exists'] = "EXISTS" if "passwd" in result.stdout else "MISSING"
    else:
        config_status['passwd_file_exists'] = "ERROR"
    
    # Check if ACL file exists
    cmd = "podman exec ghostmesh-mosquitto ls -la /mosquitto/config/acl.conf"
    result = run_command(cmd, timeout=5)
    
    if result.returncode == 0:
        config_status['acl_file_exists'] = "EXISTS" if "acl.conf" in result.stdout else "MISSING"
    else:
        config_status['acl_file_exists'] = "ERROR"
    
    return config_status


def main():
    """Main authentication test execution."""
    print("=" * 60)
    print("THE-65: GhostMesh Authentication Test")
    print("=" * 60)
    
    # Test credentials from docker-compose.yml
    test_credentials = [
        ("iot", "iotpass"),
        ("gateway", "gatewaypass"),
        ("invalid", "invalid"),
        ("", "")  # Anonymous
    ]
    
    # Step 1: Check Mosquitto configuration
    print("\n1. Checking Mosquitto configuration...")
    config_status = check_mosquitto_config()
    
    for key, value in config_status.items():
        print(f"  {key}: {value}")
    
    # Step 2: Test anonymous access
    print("\n2. Testing anonymous access...")
    anonymous_enabled = test_mqtt_anonymous_access()
    
    # Step 3: Test authenticated access
    print("\n3. Testing authenticated access...")
    auth_results = test_mqtt_authenticated_access(test_credentials)
    
    # Step 4: Test service authentication
    print("\n4. Testing service authentication...")
    service_results = test_service_authentication()
    
    # Step 5: Test ACL enforcement (if enabled)
    print("\n5. Testing ACL enforcement...")
    acl_results = test_acl_enforcement()
    
    # Step 6: Summary and recommendations
    print("\n" + "=" * 60)
    print("AUTHENTICATION TEST RESULTS")
    print("=" * 60)
    
    # Calculate overall results
    total_tests = len(auth_results) + len(service_results) + len(acl_results)
    passed_tests = sum(1 for v in {**auth_results, **service_results, **acl_results}.values() if v)
    
    print(f"Configuration Status:")
    for key, value in config_status.items():
        print(f"  {key}: {value}")
    
    print(f"\nAnonymous Access: {'ENABLED (⚠️  INSECURE)' if anonymous_enabled else 'DISABLED (✓ SECURE)'}")
    print(f"Authentication Tests: {passed_tests}/{total_tests} passed")
    
    # Security recommendations
    print(f"\n🔒 SECURITY RECOMMENDATIONS:")
    
    if anonymous_enabled:
        print("  ⚠️  CRITICAL: Disable anonymous access in production")
        print("     - Set 'allow_anonymous false' in mosquitto.conf")
        print("     - Uncomment 'password_file' and 'acl_file' lines")
    
    if config_status.get('passwd_file_exists') == 'MISSING':
        print("  ⚠️  CRITICAL: Password file is missing")
        print("     - Run 'make setup-mqtt-users' to create password file")
    
    if config_status.get('acl_file_exists') == 'MISSING':
        print("  ⚠️  CRITICAL: ACL file is missing")
        print("     - Ensure acl.conf exists and is properly configured")
    
    # Overall security assessment
    if anonymous_enabled or config_status.get('passwd_file_exists') == 'MISSING':
        print(f"\n❌ SECURITY STATUS: VULNERABLE")
        print("   Authentication is not properly configured")
        sys.exit(1)
    else:
        print(f"\n✅ SECURITY STATUS: SECURE")
        print("   Authentication is properly configured")
        sys.exit(0)


if __name__ == "__main__":
    main()
