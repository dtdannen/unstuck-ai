#!/usr/bin/env python3
"""
Custom Goose toolkit that integrates with the Unstuck MCP server
"""

import requests
import json
import logging
from typing import Dict, Any, List
try:
    from goose.toolkit.base import Toolkit, tool
except ImportError:
    # Fallback for different Goose versions
    from goose.toolkit import Toolkit, tool

logger = logging.getLogger(__name__)

class UnstuckToolkit(Toolkit):
    """Toolkit for requesting visual help from humans via Unstuck MCP server"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mcp_server_url = "http://127.0.0.1:8000"
        logger.info("UnstuckToolkit initialized")
    
    @tool
    def request_visual_help(
        self,
        screenshot_description: str,
        task_description: str,
        execute_result: bool = False
    ) -> str:
        """
        Request visual help from humans via Nostr marketplace.
        
        Args:
            screenshot_description: Description of what to screenshot
            task_description: Description of what help is needed
            execute_result: Whether to execute the instructions (mouse clicks, etc)
        
        Returns:
            Instructions from human operator or execution result
        """
        try:
            # Create the request payload
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "request_visual_help",
                    "arguments": {
                        "screenshot_description": screenshot_description,
                        "task_description": task_description,
                        "execute_result": execute_result
                    }
                },
                "id": 1
            }
            
            # Send request to MCP server
            response = requests.post(
                f"{self.mcp_server_url}/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minute timeout for human response
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
            
            if "result" in result:
                return result["result"].get("content", [{}])[0].get("text", "No response received")
            
            return "Unexpected response format from MCP server"
            
        except requests.exceptions.Timeout:
            return "Request timed out waiting for human response"
        except requests.exceptions.RequestException as e:
            return f"Network error communicating with MCP server: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in request_visual_help: {e}")
            return f"Unexpected error: {str(e)}"
    
    @tool
    def check_mcp_server_status(self) -> str:
        """Check if the MCP server is running and accessible"""
        try:
            response = requests.get(f"{self.mcp_server_url}/health", timeout=5)
            if response.status_code == 200:
                return "MCP server is running and accessible"
            else:
                return f"MCP server returned status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Cannot connect to MCP server: {str(e)}"