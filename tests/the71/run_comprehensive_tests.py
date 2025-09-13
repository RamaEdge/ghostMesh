#!/usr/bin/env python3
"""
GhostMesh Comprehensive Test Runner
Orchestrates all testing and validation for THE-71

This script runs:
1. Latency measurement tests
2. System validation tests
3. Performance monitoring
4. Generates comprehensive test report
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latency_measurement import LatencyMeasurement
from system_validation import SystemValidator
from performance_monitor import PerformanceMonitor


class ComprehensiveTestRunner:
    """Runs comprehensive testing suite for GhostMesh."""
    
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.test_results: Dict = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'test_suite': 'THE-71 Comprehensive Testing',
            'results': {}
        }
    
    def check_system_requirements(self) -> bool:
        """Check if system is ready for testing."""
        print("🔍 Checking system requirements...")
        
        try:
            # Check if services are running
            result = subprocess.run(['podman-compose', 'ps'], 
                                 capture_output=True, text=True, check=True)
            
            if 'ghostmesh' not in result.stdout.lower():
                print("❌ GhostMesh services not running")
                return False
            
            print("✅ GhostMesh services are running")
            
            # Check if MQTT broker is accessible
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.mqtt_host, self.mqtt_port))
            sock.close()
            
            if result != 0:
                print(f"❌ Cannot connect to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
                return False
            
            print("✅ MQTT broker is accessible")
            return True
            
        except Exception as e:
            print(f"❌ System check failed: {e}")
            return False
    
    def run_latency_tests(self) -> Dict:
        """Run latency measurement tests."""
        print("\n" + "="*60)
        print("🚀 RUNNING LATENCY TESTS")
        print("="*60)
        
        try:
            measurer = LatencyMeasurement(self.mqtt_host, self.mqtt_port)
            stats = measurer.run_latency_test(num_tests=10, delay=2.0)
            
            # Assess results
            latency_passed = (
                stats['avg_latency'] is not None and 
                stats['avg_latency'] <= 2.0 and 
                stats['under_2s_rate'] >= 0.95
            )
            
            result = {
                'test_name': 'Alert Latency Measurement',
                'passed': latency_passed,
                'target': '≤2s average latency, ≥95% under 2s',
                'results': stats,
                'details': [
                    f"Average latency: {stats['avg_latency']:.3f}s" if stats['avg_latency'] else "No measurements",
                    f"Under 2s rate: {stats['under_2s_rate']:.1%}" if stats['under_2s_rate'] else "No measurements",
                    f"Success rate: {stats['success_rate']:.1%}"
                ]
            }
            
            measurer.print_results(stats)
            return result
            
        except Exception as e:
            return {
                'test_name': 'Alert Latency Measurement',
                'passed': False,
                'error': str(e),
                'details': [f"❌ Test failed: {e}"]
            }
    
    def run_system_validation_tests(self) -> Dict:
        """Run system validation tests."""
        print("\n" + "="*60)
        print("🚀 RUNNING SYSTEM VALIDATION TESTS")
        print("="*60)
        
        try:
            validator = SystemValidator(self.mqtt_host, self.mqtt_port)
            results = validator.run_comprehensive_validation()
            
            # Assess overall results
            system_passed = results['failed_tests'] == 0
            
            result = {
                'test_name': 'System Validation',
                'passed': system_passed,
                'target': 'All validation tests pass',
                'results': results,
                'details': [
                    f"Total tests: {results['total_tests']}",
                    f"Passed: {results['passed_tests']}",
                    f"Failed: {results['failed_tests']}",
                    f"Success rate: {results['passed_tests']/results['total_tests']:.1%}"
                ]
            }
            
            validator.print_results(results)
            return result
            
        except Exception as e:
            return {
                'test_name': 'System Validation',
                'passed': False,
                'error': str(e),
                'details': [f"❌ Test failed: {e}"]
            }
    
    def run_performance_monitoring(self) -> Dict:
        """Run performance monitoring."""
        print("\n" + "="*60)
        print("🚀 RUNNING PERFORMANCE MONITORING")
        print("="*60)
        
        try:
            monitor = PerformanceMonitor(monitoring_duration=120)  # 2 minutes
            
            # Start monitoring
            monitor_thread = monitor.start_monitoring()
            monitor_thread.join()
            
            # Calculate statistics
            stats = monitor.calculate_statistics()
            
            # Assess performance
            performance_passed = (
                stats and 
                stats['cpu']['avg_percent'] < 80 and 
                stats['memory']['avg_percent'] < 85 and
                stats['disk']['avg_percent'] < 90
            )
            
            result = {
                'test_name': 'Performance Monitoring',
                'passed': performance_passed,
                'target': 'CPU <80%, Memory <85%, Disk <90%',
                'results': stats,
                'details': [
                    f"Average CPU: {stats['cpu']['avg_percent']:.1f}%" if stats else "No data",
                    f"Average Memory: {stats['memory']['avg_percent']:.1f}%" if stats else "No data",
                    f"Average Disk: {stats['disk']['avg_percent']:.1f}%" if stats else "No data"
                ]
            }
            
            monitor.print_results(stats)
            return result
            
        except Exception as e:
            return {
                'test_name': 'Performance Monitoring',
                'passed': False,
                'error': str(e),
                'details': [f"❌ Test failed: {e}"]
            }
    
    def run_comprehensive_tests(self) -> Dict:
        """Run all comprehensive tests."""
        print("🚀 Starting GhostMesh Comprehensive Testing (THE-71)")
        print("="*80)
        
        # Check system requirements
        if not self.check_system_requirements():
            print("❌ System requirements not met. Aborting tests.")
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'test_suite': 'THE-71 Comprehensive Testing',
                'status': 'FAILED',
                'error': 'System requirements not met',
                'results': {}
            }
        
        # Run all test suites
        test_suites = [
            self.run_latency_tests,
            self.run_system_validation_tests,
            self.run_performance_monitoring
        ]
        
        for test_suite in test_suites:
            try:
                result = test_suite()
                self.test_results['results'][result['test_name']] = result
                time.sleep(2)  # Brief pause between test suites
            except Exception as e:
                error_result = {
                    'test_name': test_suite.__name__,
                    'passed': False,
                    'error': str(e),
                    'details': [f"❌ Test suite failed: {e}"]
                }
                self.test_results['results'][error_result['test_name']] = error_result
        
        # Calculate overall results
        total_tests = len(self.test_results['results'])
        passed_tests = sum(1 for r in self.test_results['results'].values() if r['passed'])
        failed_tests = total_tests - passed_tests
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED'
        }
        
        return self.test_results
    
    def print_final_report(self):
        """Print comprehensive final test report."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT - THE-71")
        print("="*80)
        
        print(f"Test Suite: {self.test_results['test_suite']}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        
        if 'summary' in self.test_results:
            summary = self.test_results['summary']
            print(f"\nOverall Results:")
            print(f"  Total Tests: {summary['total_tests']}")
            print(f"  Passed: {summary['passed_tests']}")
            print(f"  Failed: {summary['failed_tests']}")
            print(f"  Success Rate: {summary['success_rate']:.1%}")
            print(f"  Status: {summary['overall_status']}")
        
        print(f"\nDetailed Results:")
        print("-" * 80)
        
        for test_name, result in self.test_results['results'].items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{status} - {test_name}")
            
            if 'target' in result:
                print(f"  Target: {result['target']}")
            
            for detail in result.get('details', []):
                print(f"  {detail}")
            
            if 'error' in result:
                print(f"  Error: {result['error']}")
        
        # Acceptance Criteria Assessment
        print(f"\n📋 ACCEPTANCE CRITERIA ASSESSMENT:")
        print("-" * 80)
        
        criteria = {
            'Alert latency consistently under 2 seconds': False,
            'False positive rate within acceptable limits': False,
            'System recovers gracefully from failures': False,
            'Edge cases handled properly': False,
            'Performance metrics within Pi 5 limits': False
        }
        
        # Check each criterion based on test results
        for test_name, result in self.test_results['results'].items():
            if test_name == 'Alert Latency Measurement' and result['passed']:
                criteria['Alert latency consistently under 2 seconds'] = True
            elif test_name == 'System Validation' and result['passed']:
                criteria['False positive rate within acceptable limits'] = True
                criteria['System recovers gracefully from failures'] = True
                criteria['Edge cases handled properly'] = True
            elif test_name == 'Performance Monitoring' and result['passed']:
                criteria['Performance metrics within Pi 5 limits'] = True
        
        for criterion, met in criteria.items():
            status = "✅" if met else "❌"
            print(f"  {status} {criterion}")
        
        # Final assessment
        all_criteria_met = all(criteria.values())
        if all_criteria_met:
            print(f"\n🎉 ALL ACCEPTANCE CRITERIA MET!")
            print(f"✅ THE-71 Comprehensive Testing and Validation: PASSED")
        else:
            print(f"\n⚠️  SOME ACCEPTANCE CRITERIA NOT MET")
            print(f"❌ THE-71 Comprehensive Testing and Validation: FAILED")
        
        return all_criteria_met
    
    def save_report(self, filename: str = None):
        """Save test report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ghostmesh_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\n📄 Test report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")


def main():
    """Main function to run comprehensive tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostMesh Comprehensive Test Runner (THE-71)')
    parser.add_argument('--host', default='localhost', help='MQTT broker host')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--save-report', action='store_true', help='Save detailed report to JSON file')
    
    args = parser.parse_args()
    
    # Create and run comprehensive tests
    runner = ComprehensiveTestRunner(args.host, args.port)
    
    try:
        # Run all tests
        results = runner.run_comprehensive_tests()
        
        # Print final report
        all_passed = runner.print_final_report()
        
        # Save report if requested
        if args.save_report:
            runner.save_report()
        
        # Return exit code
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
