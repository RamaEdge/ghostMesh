#!/usr/bin/env python3
"""
GhostMesh Performance Monitor
Monitors resource usage and performance metrics for Pi 5 optimization

This tool monitors:
- CPU usage across all services
- Memory consumption
- Network I/O
- Disk I/O
- Service-specific metrics
"""

import time
import psutil
import subprocess
import json
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests


class PerformanceMonitor:
    """Monitors GhostMesh system performance and resource usage."""
    
    def __init__(self, monitoring_duration: int = 300):  # 5 minutes default
        self.monitoring_duration = monitoring_duration
        self.metrics: List[Dict] = []
        self.running = False
        self.lock = threading.Lock()
        
    def get_system_metrics(self) -> Dict:
        """Get current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = None
                if 'cpu_thermal' in temps:
                    cpu_temp = temps['cpu_thermal'][0].current
                elif 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
            except:
                cpu_temp = None
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'temperature_c': cpu_temp
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'percent': memory.percent,
                    'swap_total_gb': swap.total / (1024**3),
                    'swap_used_gb': swap.used / (1024**3),
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent': (disk.used / disk.total) * 100,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            }
        except Exception as e:
            print(f"❌ Error getting system metrics: {e}")
            return None
    
    def get_container_metrics(self) -> Dict:
        """Get metrics for GhostMesh containers."""
        try:
            # Get container stats using podman
            result = subprocess.run([
                'podman', 'stats', '--no-stream', '--format', 'json'
            ], capture_output=True, text=True, check=True)
            
            containers = json.loads(result.stdout)
            ghostmesh_containers = {}
            
            for container in containers:
                name = container.get('Name', '')
                if 'ghostmesh' in name.lower():
                    ghostmesh_containers[name] = {
                        'cpu_percent': float(container.get('CPUPerc', '0%').rstrip('%')),
                        'memory_usage': container.get('MemUsage', '0B'),
                        'memory_percent': float(container.get('MemPerc', '0%').rstrip('%')),
                        'net_io': container.get('NetIO', '0B'),
                        'block_io': container.get('BlockIO', '0B'),
                        'pids': int(container.get('PIDs', '0'))
                    }
            
            return ghostmesh_containers
            
        except Exception as e:
            print(f"❌ Error getting container metrics: {e}")
            return {}
    
    def get_service_health(self) -> Dict:
        """Check health of GhostMesh services."""
        services = {
            'dashboard': {'port': 8501, 'path': '/_stcore/health'},
            'llm-server': {'port': 8080, 'path': '/health'},
            'mosquitto': {'port': 1883, 'path': None}  # MQTT doesn't have HTTP health
        }
        
        health_status = {}
        
        for service, config in services.items():
            try:
                if config['path']:
                    # HTTP health check
                    response = requests.get(
                        f"http://localhost:{config['port']}{config['path']}",
                        timeout=5
                    )
                    health_status[service] = {
                        'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                        'response_time_ms': response.elapsed.total_seconds() * 1000
                    }
                else:
                    # MQTT health check (basic port check)
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex(('localhost', config['port']))
                    sock.close()
                    
                    health_status[service] = {
                        'status': 'healthy' if result == 0 else 'unhealthy',
                        'response_time_ms': None
                    }
                    
            except Exception as e:
                health_status[service] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return health_status
    
    def monitor_loop(self):
        """Main monitoring loop."""
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.monitoring_duration:
            try:
                # Get all metrics
                system_metrics = self.get_system_metrics()
                container_metrics = self.get_container_metrics()
                service_health = self.get_service_health()
                
                if system_metrics:
                    combined_metrics = {
                        **system_metrics,
                        'containers': container_metrics,
                        'services': service_health
                    }
                    
                    with self.lock:
                        self.metrics.append(combined_metrics)
                
                # Wait before next measurement
                time.sleep(10)  # 10-second intervals
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(10)
    
    def start_monitoring(self):
        """Start performance monitoring."""
        print(f"🚀 Starting performance monitoring for {self.monitoring_duration} seconds...")
        self.running = True
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.running = False
        print("⏹️  Performance monitoring stopped")
    
    def calculate_statistics(self) -> Dict:
        """Calculate performance statistics from collected metrics."""
        with self.lock:
            if not self.metrics:
                return {}
            
            # Extract time series data
            timestamps = [m['timestamp'] for m in self.metrics]
            cpu_values = [m['cpu']['percent'] for m in self.metrics]
            memory_values = [m['memory']['percent'] for m in self.metrics]
            disk_values = [m['disk']['percent'] for m in self.metrics]
            
            # Calculate statistics
            stats = {
                'monitoring_duration_seconds': len(self.metrics) * 10,  # 10-second intervals
                'total_measurements': len(self.metrics),
                'cpu': {
                    'avg_percent': sum(cpu_values) / len(cpu_values),
                    'max_percent': max(cpu_values),
                    'min_percent': min(cpu_values)
                },
                'memory': {
                    'avg_percent': sum(memory_values) / len(memory_values),
                    'max_percent': max(memory_values),
                    'min_percent': min(memory_values)
                },
                'disk': {
                    'avg_percent': sum(disk_values) / len(disk_values),
                    'max_percent': max(disk_values),
                    'min_percent': min(disk_values)
                },
                'service_health': self._analyze_service_health(),
                'container_performance': self._analyze_container_performance()
            }
            
            return stats
    
    def _analyze_service_health(self) -> Dict:
        """Analyze service health over monitoring period."""
        with self.lock:
            service_health_summary = {}
            
            for service in ['dashboard', 'llm-server', 'mosquitto']:
                healthy_count = 0
                total_count = 0
                
                for metric in self.metrics:
                    if 'services' in metric and service in metric['services']:
                        total_count += 1
                        if metric['services'][service]['status'] == 'healthy':
                            healthy_count += 1
                
                if total_count > 0:
                    service_health_summary[service] = {
                        'uptime_percent': (healthy_count / total_count) * 100,
                        'healthy_checks': healthy_count,
                        'total_checks': total_count
                    }
            
            return service_health_summary
    
    def _analyze_container_performance(self) -> Dict:
        """Analyze container performance over monitoring period."""
        with self.lock:
            container_summary = {}
            
            # Get all unique container names
            all_containers = set()
            for metric in self.metrics:
                if 'containers' in metric:
                    all_containers.update(metric['containers'].keys())
            
            for container in all_containers:
                cpu_values = []
                memory_values = []
                
                for metric in self.metrics:
                    if 'containers' in metric and container in metric['containers']:
                        cpu_values.append(metric['containers'][container]['cpu_percent'])
                        memory_values.append(metric['containers'][container]['memory_percent'])
                
                if cpu_values:
                    container_summary[container] = {
                        'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                        'max_cpu_percent': max(cpu_values),
                        'avg_memory_percent': sum(memory_values) / len(memory_values),
                        'max_memory_percent': max(memory_values)
                    }
            
            return container_summary
    
    def print_results(self, stats: Dict):
        """Print formatted performance results."""
        print("\n" + "="*80)
        print("📊 PERFORMANCE MONITORING RESULTS")
        print("="*80)
        
        if not stats:
            print("❌ No performance data collected")
            return
        
        print(f"Monitoring Duration: {stats['monitoring_duration_seconds']} seconds")
        print(f"Total Measurements: {stats['total_measurements']}")
        
        # System Performance
        print(f"\n🖥️  System Performance:")
        print(f"  CPU Usage:")
        print(f"    Average: {stats['cpu']['avg_percent']:.1f}%")
        print(f"    Maximum: {stats['cpu']['max_percent']:.1f}%")
        print(f"    Minimum: {stats['cpu']['min_percent']:.1f}%")
        
        print(f"  Memory Usage:")
        print(f"    Average: {stats['memory']['avg_percent']:.1f}%")
        print(f"    Maximum: {stats['memory']['max_percent']:.1f}%")
        print(f"    Minimum: {stats['memory']['min_percent']:.1f}%")
        
        print(f"  Disk Usage:")
        print(f"    Average: {stats['disk']['avg_percent']:.1f}%")
        print(f"    Maximum: {stats['disk']['max_percent']:.1f}%")
        print(f"    Minimum: {stats['disk']['min_percent']:.1f}%")
        
        # Service Health
        print(f"\n🏥 Service Health:")
        for service, health in stats['service_health'].items():
            status = "✅" if health['uptime_percent'] >= 95 else "⚠️" if health['uptime_percent'] >= 90 else "❌"
            print(f"  {status} {service}: {health['uptime_percent']:.1f}% uptime ({health['healthy_checks']}/{health['total_checks']})")
        
        # Container Performance
        print(f"\n🐳 Container Performance:")
        for container, perf in stats['container_performance'].items():
            print(f"  {container}:")
            print(f"    CPU: {perf['avg_cpu_percent']:.1f}% avg, {perf['max_cpu_percent']:.1f}% max")
            print(f"    Memory: {perf['avg_memory_percent']:.1f}% avg, {perf['max_memory_percent']:.1f}% max")
        
        # Performance Assessment
        print(f"\n📈 Performance Assessment:")
        
        # Check if within Pi 5 limits
        cpu_ok = stats['cpu']['avg_percent'] < 80
        memory_ok = stats['memory']['avg_percent'] < 85
        disk_ok = stats['disk']['avg_percent'] < 90
        
        if cpu_ok and memory_ok and disk_ok:
            print("✅ System performance within Pi 5 limits")
        else:
            print("⚠️  System performance may exceed Pi 5 limits:")
            if not cpu_ok:
                print(f"  - CPU usage high: {stats['cpu']['avg_percent']:.1f}%")
            if not memory_ok:
                print(f"  - Memory usage high: {stats['memory']['avg_percent']:.1f}%")
            if not disk_ok:
                print(f"  - Disk usage high: {stats['disk']['avg_percent']:.1f}%")


def main():
    """Main function to run performance monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostMesh Performance Monitor')
    parser.add_argument('--duration', type=int, default=300, help='Monitoring duration in seconds')
    
    args = parser.parse_args()
    
    # Create and run performance monitor
    monitor = PerformanceMonitor(args.duration)
    
    try:
        # Start monitoring
        monitor_thread = monitor.start_monitoring()
        
        # Wait for monitoring to complete
        monitor_thread.join()
        
        # Calculate and print results
        stats = monitor.calculate_statistics()
        monitor.print_results(stats)
        
        # Return exit code based on performance
        if stats and stats['cpu']['avg_percent'] < 80 and stats['memory']['avg_percent'] < 85:
            return 0  # Good performance
        else:
            return 1  # Performance issues
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring interrupted by user")
        monitor.stop_monitoring()
        return 0
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
