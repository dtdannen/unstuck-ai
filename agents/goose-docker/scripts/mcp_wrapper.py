#!/usr/bin/env python3
"""
MCP Wrapper for Goose
This script starts MCP servers and provides a bridge for Goose to access them
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path

class MCPServerManager:
    def __init__(self, config_path="/home/goose/.config/mcp_servers.json"):
        self.config_path = config_path
        self.servers = {}
        self.processes = {}
        
    def load_config(self):
        """Load MCP server configuration"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.servers = config.get('mcpServers', {})
            
    def start_server(self, name, server_config):
        """Start an individual MCP server"""
        try:
            # Set up environment
            env = os.environ.copy()
            env.update(server_config.get('env', {}))
            
            # Build command
            cmd = [server_config['command']] + server_config.get('args', [])
            
            # Set working directory
            cwd = server_config.get('cwd', None)
            
            print(f"Starting MCP server '{name}': {' '.join(cmd)}")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[name] = process
            print(f"✅ Started MCP server '{name}' (PID: {process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to start MCP server '{name}': {e}")
            
    def start_all(self):
        """Start all configured MCP servers"""
        self.load_config()
        
        for name, config in self.servers.items():
            # Skip certain servers for now
            if name in ['web-search', 'goose-computer']:
                print(f"⏭️  Skipping '{name}' server (not available)")
                continue
                
            self.start_server(name, config)
            
    def stop_all(self):
        """Stop all running MCP servers"""
        for name, process in self.processes.items():
            try:
                process.terminate()
                print(f"Stopped MCP server '{name}'")
            except:
                pass

if __name__ == "__main__":
    manager = MCPServerManager()
    
    try:
        print("🚀 Starting MCP servers...")
        manager.start_all()
        
        # Keep running
        print("✅ MCP servers are running. Press Ctrl+C to stop.")
        while True:
            # Check if any processes have died
            for name, process in list(manager.processes.items()):
                if process.poll() is not None:
                    print(f"⚠️  MCP server '{name}' died with code {process.returncode}")
                    # Try to restart it
                    if name in manager.servers:
                        manager.start_server(name, manager.servers[name])
            
            asyncio.run(asyncio.sleep(5))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping MCP servers...")
        manager.stop_all()