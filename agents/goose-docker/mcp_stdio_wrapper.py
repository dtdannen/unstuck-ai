#!/usr/bin/env python3
"""
MCP stdio wrapper that connects to the FastMCP server running on port 8000
and provides a stdio interface for Goose to communicate with it.
"""

import sys
import json
import requests
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/tmp/mcp_stdio_wrapper.log'
)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://127.0.0.1:8000"

class MCPStdioWrapper:
    def __init__(self):
        self.session = requests.Session()
        logger.info("MCP stdio wrapper initialized")
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC request and forward to MCP server"""
        try:
            # Forward the request to the MCP server
            response = self.session.post(
                f"{MCP_SERVER_URL}/",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request.get("id")
            }
    
    def run(self):
        """Main loop to handle stdio communication"""
        logger.info("Starting stdio wrapper main loop")
        
        # Send initial capabilities
        capabilities = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "capabilities": {
                    "tools": [{
                        "name": "request_visual_help",
                        "description": "Request visual help from humans via Nostr marketplace",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "screenshot_description": {"type": "string"},
                                "task_description": {"type": "string"},
                                "execute_result": {"type": "boolean", "default": False}
                            },
                            "required": ["screenshot_description", "task_description"]
                        }
                    }]
                }
            }
        }
        
        print(json.dumps(capabilities))
        sys.stdout.flush()
        
        # Main loop
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")
                
                response = self.handle_request(request)
                logger.debug(f"Sending response: {response}")
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    wrapper = MCPStdioWrapper()
    wrapper.run()