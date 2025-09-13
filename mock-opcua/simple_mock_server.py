#!/usr/bin/env python3
"""
Simple GhostMesh Mock OPC UA Server
Minimal implementation for development and testing
"""

import asyncio
import logging
import random
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

from asyncua import Server, ua


class SimpleMockOPCUAServer:
    """Simple mock OPC UA server simulating industrial equipment"""
    
    def __init__(self):
        self.server = None
        self.running = False
        self.nodes: Dict[str, Any] = {}
        
        # Equipment simulation data
        self.equipment_data = {
            "Press01": {
                "temperature": {"value": 45.0, "min": 20.0, "max": 80.0, "trend": 0.1},
                "pressure": {"value": 12.5, "min": 0.0, "max": 25.0, "trend": 0.05},
                "vibration": {"value": 2.1, "min": 0.0, "max": 10.0, "trend": 0.02},
                "status": {"value": "Running", "states": ["Running", "Stopped", "Maintenance", "Error"]}
            },
            "Press02": {
                "temperature": {"value": 42.0, "min": 20.0, "max": 80.0, "trend": -0.1},
                "pressure": {"value": 11.8, "min": 0.0, "max": 25.0, "trend": 0.03},
                "vibration": {"value": 1.8, "min": 0.0, "max": 10.0, "trend": -0.01},
                "status": {"value": "Running", "states": ["Running", "Stopped", "Maintenance", "Error"]}
            },
            "Conveyor01": {
                "speed": {"value": 15.5, "min": 0.0, "max": 30.0, "trend": 0.0},
                "load": {"value": 125.0, "min": 0.0, "max": 500.0, "trend": 0.5},
                "status": {"value": "Running", "states": ["Running", "Stopped", "Maintenance", "Error"]}
            }
        }
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('simple_mock_opcua_server.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def create_server(self):
        """Create and configure OPC UA server"""
        self.server = Server()
        await self.server.init()
        
        # Set server endpoint
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840")
        
        # Set server name
        self.server.set_server_name("GhostMesh Simple Mock OPC UA Server")
        
        # Setup namespace
        ns_idx = await self.server.register_namespace("http://ghostmesh.io/industrial")
        
        # Create equipment objects and variables
        await self.create_equipment_nodes(ns_idx)
        
        self.logger.info("OPC UA server created and configured")
    
    async def create_equipment_nodes(self, ns_idx: int):
        """Create equipment nodes and variables"""
        # Create root equipment folder
        equipment_folder = await self.server.nodes.objects.add_folder(ns_idx, "Equipment")
        
        for equipment_name, signals in self.equipment_data.items():
            # Create equipment object
            equipment_obj = await equipment_folder.add_object(ns_idx, equipment_name)
            
            # Create variables for each signal
            for signal_name, signal_data in signals.items():
                if signal_name == "status":
                    # String variable for status
                    var = await equipment_obj.add_variable(
                        ns_idx, signal_name, signal_data["value"]
                    )
                else:
                    # Numeric variables
                    var = await equipment_obj.add_variable(
                        ns_idx, signal_name, signal_data["value"]
                    )
                
                # Set variable properties
                await var.set_writable()
                
                # Store node reference
                node_id = f"ns={ns_idx};s={equipment_name}.{signal_name.title()}"
                self.nodes[node_id] = var
                
                self.logger.info(f"Created node: {node_id}")
    
    def update_equipment_data(self):
        """Update equipment simulation data with realistic variations"""
        for equipment_name, signals in self.equipment_data.items():
            for signal_name, signal_data in signals.items():
                if signal_name == "status":
                    # Occasionally change status (5% chance every update)
                    if random.random() < 0.05:
                        current_states = signal_data["states"]
                        current_idx = current_states.index(signal_data["value"])
                        # Usually stay in current state or move to adjacent states
                        if random.random() < 0.8:
                            signal_data["value"] = current_states[current_idx]
                        else:
                            # Move to different state
                            new_idx = (current_idx + random.choice([-1, 1])) % len(current_states)
                            signal_data["value"] = current_states[new_idx]
                else:
                    # Update numeric values with trend and random variation
                    trend = signal_data["trend"]
                    variation = random.gauss(0, 0.1)  # Small random variation
                    
                    new_value = signal_data["value"] + trend + variation
                    
                    # Apply bounds
                    new_value = max(signal_data["min"], min(signal_data["max"], new_value))
                    
                    # Occasionally reverse trend direction
                    if random.random() < 0.1:
                        signal_data["trend"] = -signal_data["trend"]
                    
                    signal_data["value"] = new_value
    
    async def update_node_values(self):
        """Update OPC UA node values with current simulation data"""
        for node_id, node in self.nodes.items():
            try:
                # Extract equipment and signal from node ID
                parts = node_id.split('.')
                if len(parts) >= 2:
                    equipment_name = parts[0].split(';s=')[1]
                    signal_name = parts[1].lower()
                    
                    # Get current value from simulation data
                    if equipment_name in self.equipment_data:
                        equipment_data = self.equipment_data[equipment_name]
                        if signal_name in equipment_data:
                            value = equipment_data[signal_name]["value"]
                            
                            # Update the OPC UA node
                            await node.write_value(value)
                            
                            self.logger.debug(f"Updated {node_id} = {value}")
                            
            except Exception as e:
                self.logger.error(f"Failed to update node {node_id}: {e}")
    
    async def run(self):
        """Main server loop"""
        self.logger.info("Starting GhostMesh Simple Mock OPC UA Server")
        
        try:
            # Create server
            await self.create_server()
            
            # Start server
            async with self.server:
                self.logger.info("OPC UA server started on opc.tcp://0.0.0.0:4840")
                self.logger.info("Available endpoints:")
                endpoints = await self.server.get_endpoints()
                for endpoint in endpoints:
                    self.logger.info(f"  - {endpoint}")
                
                self.running = True
                
                # Main simulation loop
                while self.running:
                    # Update simulation data
                    self.update_equipment_data()
                    
                    # Update OPC UA nodes
                    await self.update_node_values()
                    
                    # Wait before next update
                    await asyncio.sleep(1.0)  # Update every second
                    
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down simple mock OPC UA server...")
        self.running = False
        
        if self.server and hasattr(self.server, 'stop'):
            try:
                await self.server.stop()
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")
        
        self.logger.info("Simple mock OPC UA server shutdown complete")


async def main():
    """Main entry point"""
    server = SimpleMockOPCUAServer()
    
    try:
        await server.run()
    except KeyboardInterrupt:
        server.logger.info("Received keyboard interrupt")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
