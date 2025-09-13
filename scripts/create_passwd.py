#!/usr/bin/env python3
"""
Create MQTT password file using Python
"""

import subprocess
import os

def create_password_file():
    """Create password file with all required users"""
    
    # Define users and passwords
    users = {
        "iot": "iotpass",
        "gateway": "gatewaypass", 
        "detector": "detectorpass",
        "explainer": "explainerpass",
        "policy": "policypass",
        "dashboard": "dashboard123"
    }
    
    # Ensure mosquitto directory exists
    os.makedirs("mosquitto", exist_ok=True)
    
    # Remove existing password file
    if os.path.exists("mosquitto/passwd"):
        os.remove("mosquitto/passwd")
    
    # Create password file using mosquitto_passwd
    for username, password in users.items():
        cmd = [
            "podman", "run", "--rm",
            "-v", f"{os.getcwd()}/mosquitto:/tmp/mosquitto",
            "eclipse-mosquitto:2",
            "mosquitto_passwd", "-b", "/tmp/mosquitto/passwd", username, password
        ]
        
        print(f"Creating user: {username}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating user {username}: {result.stderr}")
        else:
            print(f"Successfully created user: {username}")
    
    print("\nPassword file created successfully!")
    print("Users created:")
    for username in users.keys():
        print(f"  - {username}")

if __name__ == "__main__":
    create_password_file()

