#!/usr/bin/env python3
"""
THE-66 Test Runner

Simple test runner for THE-66 anomaly injection and alert validation testing.
"""

import sys
import os
import subprocess
import time

# Add the tests directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_services_running():
    """Check if required services are running."""
    print("Checking if GhostMesh services are running...")
    
    try:
        # Check if services are running using make status
        result = subprocess.run(["make", "status"], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), "../.."))
        if result.returncode == 0:
            print("✓ Services are running")
            return True
        else:
            print("✗ Services are not running")
            print("Please run 'make start' first")
            return False
    except Exception as e:
        print(f"Error checking services: {e}")
        return False

def run_anomaly_validation_test():
    """Run the anomaly validation test."""
    print("\n" + "="*60)
    print("THE-66: Anomaly Injection and Alert Validation Testing")
    print("="*60)
    
    try:
        # Import and run the test
        from test_anomaly_validation import AnomalyValidationTester
        
        tester = AnomalyValidationTester()
        results = tester.run_comprehensive_test()
        
        if "error" in results:
            print(f"Test failed: {results['error']}")
            return False
        
        # Print summary
        summary = results.get("test_summary", {})
        print(f"\nTest Summary:")
        print(f"  Passed: {summary.get('total_passed', 0)}")
        print(f"  Failed: {summary.get('total_failed', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        return summary.get('total_failed', 0) == 0
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

def main():
    """Main test runner function."""
    print("THE-66 Test Runner")
    print("==================")
    
    # Check if services are running
    if not check_services_running():
        print("\nPlease start the GhostMesh services first:")
        print("  make start")
        return 1
    
    # Run the anomaly validation test
    success = run_anomaly_validation_test()
    
    if success:
        print("\n✓ All THE-66 tests passed!")
        return 0
    else:
        print("\n✗ Some THE-66 tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
