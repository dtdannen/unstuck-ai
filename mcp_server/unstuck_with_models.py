import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR

# Initialize MCP server
mcp = FastMCP("unstuck-ai")

# Load environment variables
load_dotenv()

# Define Pydantic models
class VisualHelpRequest(BaseModel):
    description: str
    screenshot_url: str
    max_price_sats: Optional[int] = None

class JobResult(BaseModel):
    job_id: str
    offers: List[Dict[str, Any]]
    selected_offer: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None

@mcp.tool()
def request_visual_help(description: str = "", screenshot_url: str = "", max_price_sats: Optional[int] = None) -> Dict[str, Any]:
    """
    Request visual computer interaction help from humans through Nostr.

    This tool sends a request to Nostr relays asking for help with a visual computer interaction task.
    It waits for offers from human helpers, selects the cheapest valid offer (if max_price_sats is set),
    and returns the result.

    Args:
        description: A detailed description of what help is needed
        screenshot_url: URL to a screenshot or image showing the visual context
        max_price_sats: Maximum price willing to pay in satoshis (optional)

    Returns:
        A dictionary containing the job ID, offers received, selected offer, and result
    """
    try:
        # Create the request using model_construct instead of direct initialization
        request_data = {
            "description": description,
            "screenshot_url": screenshot_url,
            "max_price_sats": max_price_sats
        }
        request = VisualHelpRequest.model_construct(**request_data)
        
        # For now, just return a mock response
        result_data = {
            "job_id": "mock-job-id",
            "offers": [],
            "selected_offer": None,
            "result": {
                "content": f"Mock response for: {request.description}",
                "screenshot_url": request.screenshot_url
            }
        }
        
        # Create the result using model_construct
        result = JobResult.model_construct(**result_data)
        
        # Return as a dictionary
        return result.model_dump()
    except Exception as e:
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Error requesting visual help: {str(e)}")
        )

if __name__ == "__main__":
    mcp.run()
