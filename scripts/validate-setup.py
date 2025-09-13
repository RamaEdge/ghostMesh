#!/usr/bin/env python3
"""
GhostMesh Setup Validation Script

This script validates the GhostMesh system setup and configuration.
It checks dependencies, configuration files, network connectivity, and service health.

Usage:
    python3 scripts/validate-setup.py [--verbose] [--fix]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class GhostMeshValidator:
    """GhostMesh system validator."""
    
    def __init__(self, verbose: bool = False, fix: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.fixes_applied: List[str] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with appropriate level."""
        if level == "ERROR":
            self.errors.append(message)
            print(f"❌ ERROR: {message}")
        elif level == "WARNING":
            self.warnings.append(message)
            print(f"⚠️  WARNING: {message}")
        elif level == "FIX":
            self.fixes_applied.append(message)
            print(f"🔧 FIX: {message}")
        elif self.verbose or level == "INFO":
            print(f"ℹ️  {message}")
    
    def run_command(self, command: str, check: bool = True) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
    
    def check_docker_available(self) -> bool:
        """Check if Docker or Podman is available."""
        self.log("Checking container runtime availability...")
        
        # Check for Podman first (preferred)
        exit_code, stdout, stderr = self.run_command("podman --version", check=False)
        if exit_code == 0:
            self.log(f"Podman found: {stdout.strip()}")
            return True
        
        # Check for Docker
        exit_code, stdout, stderr = self.run_command("docker --version", check=False)
        if exit_code == 0:
            self.log(f"Docker found: {stdout.strip()}")
            return True
        
        self.log("Neither Podman nor Docker found", "ERROR")
        return False
    
    def check_compose_available(self) -> bool:
        """Check if Docker Compose or Podman Compose is available."""
        self.log("Checking compose availability...")
        
        # Check for podman-compose first
        exit_code, stdout, stderr = self.run_command("podman-compose --version", check=False)
        if exit_code == 0:
            self.log(f"Podman Compose found: {stdout.strip()}")
            return True
        
        # Check for docker-compose
        exit_code, stdout, stderr = self.run_command("docker-compose --version", check=False)
        if exit_code == 0:
            self.log(f"Docker Compose found: {stdout.strip()}")
            return True
        
        self.log("Neither Podman Compose nor Docker Compose found", "ERROR")
        return False
    
    def check_required_files(self) -> bool:
        """Check if all required configuration files exist."""
        self.log("Checking required configuration files...")
        
        required_files = [
            "docker-compose.yml",
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
            "mosquitto/mosquitto.conf",
            "mosquitto/acl.conf",
            "opcua2mqtt/mapping.yaml",
            "Makefile"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
            else:
                self.log(f"✓ {file_path} exists")
        
        if missing_files:
            self.log(f"Missing required files: {', '.join(missing_files)}", "ERROR")
            return False
        
        return True
    
    def check_mqtt_configuration(self) -> bool:
        """Check MQTT broker configuration."""
        self.log("Checking MQTT configuration...")
        
        # Check if password file exists
        if not Path("mosquitto/passwd").exists():
            if self.fix:
                self.log("Creating MQTT password file...", "FIX")
                exit_code, stdout, stderr = self.run_command("make setup-mqtt-users")
                if exit_code == 0:
                    self.log("MQTT password file created successfully", "FIX")
                else:
                    self.log(f"Failed to create MQTT password file: {stderr}", "ERROR")
                    return False
            else:
                self.log("MQTT password file missing. Run 'make setup-mqtt-users'", "ERROR")
                return False
        
        # Check password file permissions
        passwd_file = Path("mosquitto/passwd")
        if passwd_file.exists():
            stat = passwd_file.stat()
            if stat.st_mode & 0o777 > 0o644:
                self.log("MQTT password file has overly permissive permissions", "WARNING")
        
        return True
    
    def check_llm_model(self) -> bool:
        """Check if LLM model is available."""
        self.log("Checking LLM model availability...")
        
        # Check if model directory exists
        model_dir = Path("llm-server/models")
        if not model_dir.exists():
            self.log("LLM model directory not found", "WARNING")
            return True  # Not critical for basic validation
        
        # Check for model file
        model_files = list(model_dir.glob("*.gguf"))
        if not model_files:
            self.log("No LLM model files found. Model will be downloaded on first run.", "WARNING")
        else:
            self.log(f"Found LLM model files: {[f.name for f in model_files]}")
        
        return True
    
    def check_network_ports(self) -> bool:
        """Check if required ports are available."""
        self.log("Checking network port availability...")
        
        required_ports = [1883, 4840, 8080, 8501]
        occupied_ports = []
        
        for port in required_ports:
            exit_code, stdout, stderr = self.run_command(f"netstat -tulpn | grep :{port}", check=False)
            if exit_code == 0 and stdout.strip():
                occupied_ports.append(port)
                self.log(f"Port {port} is already in use", "WARNING")
            else:
                self.log(f"✓ Port {port} is available")
        
        if occupied_ports:
            self.log(f"Occupied ports: {occupied_ports}. Services may conflict.", "WARNING")
        
        return True
    
    def check_system_resources(self) -> bool:
        """Check system resource availability."""
        self.log("Checking system resources...")
        
        # Check available memory
        exit_code, stdout, stderr = self.run_command("free -h")
        if exit_code == 0:
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                mem_info = lines[1].split()
                if len(mem_info) >= 7:
                    available_mem = mem_info[6]
                    self.log(f"Available memory: {available_mem}")
        
        # Check available disk space
        exit_code, stdout, stderr = self.run_command("df -h .")
        if exit_code == 0:
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                if len(disk_info) >= 4:
                    available_space = disk_info[3]
                    self.log(f"Available disk space: {available_space}")
        
        return True
    
    def validate_compose_config(self) -> bool:
        """Validate Docker Compose configuration."""
        self.log("Validating Docker Compose configuration...")
        
        # Check if compose config is valid
        exit_code, stdout, stderr = self.run_command("docker-compose config", check=False)
        if exit_code != 0:
            self.log(f"Invalid Docker Compose configuration: {stderr}", "ERROR")
            return False
        
        self.log("✓ Docker Compose configuration is valid")
        return True
    
    def check_service_health(self) -> bool:
        """Check if services are running and healthy."""
        self.log("Checking service health...")
        
        # Check if services are running
        exit_code, stdout, stderr = self.run_command("docker-compose ps", check=False)
        if exit_code != 0:
            self.log("Services are not running. Start them with 'make start'", "WARNING")
            return True  # Not an error if services aren't running
        
        # Parse service status
        lines = stdout.strip().split('\n')
        running_services = 0
        total_services = 0
        
        for line in lines:
            if 'ghostmesh-' in line and 'Up' in line:
                running_services += 1
                total_services += 1
            elif 'ghostmesh-' in line:
                total_services += 1
        
        if total_services > 0:
            self.log(f"Services running: {running_services}/{total_services}")
            if running_services < total_services:
                self.log("Some services are not running", "WARNING")
        
        return True
    
    def run_validation(self) -> bool:
        """Run all validation checks."""
        self.log("Starting GhostMesh setup validation...")
        self.log("=" * 50)
        
        checks = [
            ("Container Runtime", self.check_docker_available),
            ("Compose Tool", self.check_compose_available),
            ("Required Files", self.check_required_files),
            ("MQTT Configuration", self.check_mqtt_configuration),
            ("LLM Model", self.check_llm_model),
            ("Network Ports", self.check_network_ports),
            ("System Resources", self.check_system_resources),
            ("Compose Configuration", self.validate_compose_config),
            ("Service Health", self.check_service_health),
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
        self.log("VALIDATION SUMMARY")
        self.log("=" * 50)
        
        if self.fixes_applied:
            self.log(f"\n🔧 Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                self.log(f"  - {fix}")
        
        if self.warnings:
            self.log(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                self.log(f"  - {warning}")
        
        if self.errors:
            self.log(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                self.log(f"  - {error}")
        
        if not self.errors:
            self.log("\n✅ All validation checks passed!")
            self.log("GhostMesh is ready to use. Run 'make start' to begin.")
        else:
            self.log(f"\n❌ Validation failed with {len(self.errors)} errors.")
            self.log("Please fix the errors above before proceeding.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate GhostMesh setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", "-f", action="store_true", help="Attempt to fix issues automatically")
    
    args = parser.parse_args()
    
    validator = GhostMeshValidator(verbose=args.verbose, fix=args.fix)
    
    try:
        success = validator.run_validation()
        validator.print_summary()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nValidation failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
