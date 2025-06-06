import os
import asyncio
import json
import time
import logging
import requests
import random
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Import PyAutoGUI for mouse control
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
    logger = logging.getLogger("unstuck-ai")
    logger.info("PyAutoGUI is available")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger = logging.getLogger("unstuck-ai")
    logger.warning("PyAutoGUI is not available")


# Functions for executing mouse actions
def execute_click(x_percent, y_percent):
    """
    Execute a click at the specified percentage coordinates of the screen.

    Args:
        x_percent: X coordinate as a percentage of screen width (0-100)
        y_percent: Y coordinate as a percentage of screen height (0-100)
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("PyAutoGUI not available, cannot execute click")
        return False

    try:
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        logger.info(f"Screen size: {screen_width}x{screen_height}")

        # Calculate pixel coordinates
        x = int((x_percent / 100) * screen_width)
        y = int((y_percent / 100) * screen_height)
        logger.info(
            f"Executing click at coordinates: ({x}, {y}) - {x_percent}%, {y_percent}%"
        )

        # Add a small delay before executing the action
        time.sleep(0.5)

        # Move to position first, then click
        pyautogui.moveTo(x, y, duration=0.2)
        logger.info(f"Moved to position ({x}, {y})")

        # Execute the click
        pyautogui.click(x, y)
        logger.info(f"Clicked at position ({x}, {y})")

        return True
    except Exception as e:
        logger.error(f"Error executing click: {str(e)}")
        return False


def execute_double_click(x_percent, y_percent):
    """
    Execute a double-click at the specified percentage coordinates of the screen.

    Args:
        x_percent: X coordinate as a percentage of screen width (0-100)
        y_percent: Y coordinate as a percentage of screen height (0-100)
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("PyAutoGUI not available, cannot execute double-click")
        return False

    try:
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        logger.info(f"Screen size: {screen_width}x{screen_height}")

        # Calculate pixel coordinates
        x = int((x_percent / 100) * screen_width)
        y = int((y_percent / 100) * screen_height)
        logger.info(
            f"Executing double-click at coordinates: ({x}, {y}) - {x_percent}%, {y_percent}%"
        )

        # Add a small delay before executing the action
        time.sleep(0.5)

        # Move to position first, then double-click
        pyautogui.moveTo(x, y, duration=0.2)
        logger.info(f"Moved to position ({x}, {y})")

        # Execute the double-click
        pyautogui.doubleClick(x, y)
        logger.info(f"Double-clicked at position ({x}, {y})")

        return True
    except Exception as e:
        logger.error(f"Error executing double-click: {str(e)}")
        return False


def execute_drag(start_x_percent, start_y_percent, end_x_percent, end_y_percent):
    """
    Execute a drag operation from start to end coordinates (specified as percentages).

    Args:
        start_x_percent: Starting X coordinate as a percentage of screen width (0-100)
        start_y_percent: Starting Y coordinate as a percentage of screen height (0-100)
        end_x_percent: Ending X coordinate as a percentage of screen width (0-100)
        end_y_percent: Ending Y coordinate as a percentage of screen height (0-100)
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("PyAutoGUI not available, cannot execute drag")
        return False

    try:
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        logger.info(f"Screen size: {screen_width}x{screen_height}")

        # Calculate pixel coordinates
        start_x = int((start_x_percent / 100) * screen_width)
        start_y = int((start_y_percent / 100) * screen_height)
        end_x = int((end_x_percent / 100) * screen_width)
        end_y = int((end_y_percent / 100) * screen_height)

        logger.info(f"Executing drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")

        # Add a small delay before executing the action
        time.sleep(0.5)

        # Move to start position
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        logger.info(f"Moved to start position ({start_x}, {start_y})")

        # Execute the drag
        pyautogui.dragTo(end_x, end_y, duration=0.5)  # 0.5 second drag
        logger.info(f"Dragged to end position ({end_x}, {end_y})")

        return True
    except Exception as e:
        logger.error(f"Error executing drag: {str(e)}")
        return False


def execute_actions(actions_data):
    """
    Execute a series of mouse actions based on the provided JSON data.

    Args:
        actions_data: A dictionary containing actions to execute

    Returns:
        A dictionary with results of the execution
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("PyAutoGUI not available, cannot execute actions")
        return {"success": False, "error": "PyAutoGUI not available"}

    try:
        logger.info(f"Executing actions: {json.dumps(actions_data)[:200]}...")

        # Validate the input data
        if not isinstance(actions_data, dict):
            logger.error("Invalid actions data format: not a dictionary")
            return {"success": False, "error": "Invalid actions data format"}

        if "actions" not in actions_data or not isinstance(
            actions_data["actions"], list
        ):
            logger.error("Invalid actions data: 'actions' list not found")
            return {
                "success": False,
                "error": "Invalid actions data: 'actions' list not found",
            }

        # Track results for each action
        results = []

        # Execute each action
        for i, action in enumerate(actions_data["actions"]):
            try:
                action_type = action.get("type")

                if action_type == "click":
                    success = execute_click(action.get("x", 0), action.get("y", 0))
                    results.append({"index": i, "type": "click", "success": success})

                elif action_type == "doubleClick":
                    success = execute_double_click(
                        action.get("x", 0), action.get("y", 0)
                    )
                    results.append(
                        {"index": i, "type": "doubleClick", "success": success}
                    )

                elif action_type == "drag":
                    start = action.get("start", {})
                    end = action.get("end", {})
                    success = execute_drag(
                        start.get("x", 0),
                        start.get("y", 0),
                        end.get("x", 0),
                        end.get("y", 0),
                    )
                    results.append({"index": i, "type": "drag", "success": success})

                else:
                    logger.warning(f"Unknown action type: {action_type}")
                    results.append(
                        {
                            "index": i,
                            "type": action_type,
                            "success": False,
                            "error": "Unknown action type",
                        }
                    )

                # Small delay between actions
                time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error executing action {i}: {str(e)}")
                results.append(
                    {
                        "index": i,
                        "type": action.get("type", "unknown"),
                        "success": False,
                        "error": str(e),
                    }
                )

        return {"success": True, "actions_executed": len(results), "results": results}

    except Exception as e:
        logger.error(f"Error in execute_actions: {str(e)}")
        return {"success": False, "error": str(e)}


# Digital Ocean Spaces upload functionality
def upload_to_space(local_file, remote_file):
    """
    Upload a file to DigitalOcean Spaces

    Args:
        local_file (str): Path to the local file
        remote_file (str): Path in the Space where the file will be stored

    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Initialize the S3 client for DigitalOcean Spaces
        import boto3
        from botocore.exceptions import NoCredentialsError
        
        # Get credentials from environment variables
        aws_access_key = os.getenv("DIGITAL_OCEAN_SPACES_ACCESS_KEY")
        aws_secret_key = os.getenv("DIGITAL_OCEAN_SPACES_SECRET_KEY")
        region = os.getenv("DIGITAL_OCEAN_SPACES_REGION", "nyc3")
        space_name = os.getenv("DIGITAL_OCEAN_SPACE_NAME", "unstuck-goose")
        endpoint_url = f"https://{region}.digitaloceanspaces.com"
        
        # Log credential information (masked for security)
        logger.info(f"DO Spaces Access Key: {'*' * 4}{aws_access_key[-4:] if aws_access_key else 'None'}")
        logger.info(f"DO Spaces Secret Key: {'*' * 4}{aws_secret_key[-4:] if aws_secret_key else 'None'}")
        logger.info(f"DO Spaces Region: {region}")
        logger.info(f"DO Space Name: {space_name}")
        logger.info(f"DO Endpoint URL: {endpoint_url}")
        
        # Validate file exists
        if not os.path.exists(local_file):
            logger.error(f"File not found: {local_file}")
            return False
            
        # Validate credentials
        if not aws_access_key or not aws_secret_key:
            logger.error("Missing Digital Ocean Spaces credentials. Check your .env file for DIGITAL_OCEAN_SPACES_ACCESS_KEY and DIGITAL_OCEAN_SPACES_SECRET_KEY")
            return False
        
        logger.info(f"Creating S3 client for Digital Ocean Spaces...")
        s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        # Upload the file with public-read ACL to make it publicly accessible
        extra_args = {
            "ACL": "public-read",  # This makes the file publicly accessible
            "ContentType": "image/png",  # Set the appropriate content type
        }

        logger.info(f"Uploading file {local_file} to {space_name}/{remote_file}...")
        s3.upload_file(local_file, space_name, remote_file, ExtraArgs=extra_args)
        logger.info(f"Upload Successful: {local_file} -> {space_name}/{remote_file}")

        # Generate and print the public URL
        public_url = f"https://{space_name}.{region}.digitaloceanspaces.com/{remote_file}"
        logger.info(f"Public URL: {public_url}")

        return True
    except FileNotFoundError as e:
        logger.error(f"The file was not found: {local_file}")
        logger.error(f"FileNotFoundError details: {str(e)}")
        return False
    except NoCredentialsError as e:
        logger.error("Credentials not available or invalid")
        logger.error(f"NoCredentialsError details: {str(e)}")
        return False
    except boto3.exceptions.S3UploadFailedError as e:
        logger.error(f"S3 upload failed: {str(e)}")
        return False
    except boto3.exceptions.Boto3Error as e:
        logger.error(f"Boto3 error during upload: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"An error occurred during upload: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("unstuck-ai")

# Enable debug mode for detailed logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

try:
    from nostr_sdk import (
        Keys,
        Client,
        EventBuilder,
        NostrSigner,
        Kind,
        Tag,
        Filter,
        Event,
        EventId,
        HandleNotification,
        RelayMessage,
        Timestamp,
        NostrWalletConnectUri,
        Nwc,
        PayInvoiceRequest,
    )

    NOSTR_SDK_AVAILABLE = True
    logger.info("Nostr SDK is available")
except ImportError:
    NOSTR_SDK_AVAILABLE = False
    logger.warning("Nostr SDK is not available")

# Initialize MCP server
mcp = FastMCP("unstuck-ai")

# Load environment variables
load_dotenv()

# Get environment variables
NOSTR_PRIVATE_KEY = os.getenv("NOSTR_PRIVATE_KEY")
RELAY_URLS = os.getenv(
    "RELAY_URLS",
    "wss://relay.damus.io,wss://relay.supertech.ai,wss://relay.primal.net,wss://relay.dvmdash.live",
).split(",")
# Lightning node API URL
LEXE_PROXY_NODE_API_URL = os.getenv("LEXE_PROXY_NODE_API_URL", "http://localhost:5393")
# NWC key for Lightning payments
NWC_KEY = os.getenv("NWC_KEY")
# Maximum price limit for automatic payments (in sats)
MAX_AUTO_PAYMENT_SATS = 100
# Digital Ocean Spaces configuration
DIGITAL_OCEAN_SPACE_NAME = os.getenv("DIGITAL_OCEAN_SPACE_NAME", "unstuck-goose")
DIGITAL_OCEAN_REGION = os.getenv("DIGITAL_OCEAN_REGION", "nyc3")

# Initialize Nostr client and NWC if SDK is available
if NOSTR_SDK_AVAILABLE:
    keys = Keys.parse(NOSTR_PRIVATE_KEY) if NOSTR_PRIVATE_KEY else Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    logger.info(
        f"Nostr client initialized with public key: {keys.public_key().to_hex()}"
    )

    # Initialize NWC client if key is available
    nwc = None
    if NWC_KEY:
        try:
            uri = NostrWalletConnectUri.parse(NWC_KEY)
            nwc = Nwc(uri)
            logger.info("NWC client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NWC client: {str(e)}")
    else:
        logger.warning(
            "NWC_KEY not found in environment variables. Will use Lexe for payments if available."
        )

    # We'll connect to relays when needed in the request_visual_help function
    logger.info(f"Will connect to relays: {RELAY_URLS}")


# Define a notification handler class
class NotificationHandler:
    """Handler for Nostr notifications."""

    def __init__(self, event_id):
        self.event_id = event_id
        self.job_completed = asyncio.Event()
        self.offers = []
        self.result = None

    async def handle(self, relay_url, subscription_id, ev):
        event_id_hex = ev.id().to_hex()
        event_kind = ev.kind().as_u16()

        # Check if this event references our request
        is_related = False
        for tag in ev.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "e":
                if tag_vec[1] == self.event_id:
                    is_related = True
                    logger.info(
                        f"Found related event: {event_id_hex} (Kind: {event_kind})"
                    )

                    # Process the event based on its kind
                    if event_kind == 7000:  # Job response event (offer)
                        logger.info(f"Received kind 7000 offer event: {event_id_hex}")
                        await self._process_offer_event(ev)
                    elif (
                        event_kind == 6109
                    ):  # Specific job result event we're waiting for
                        logger.info(f"Received kind 6109 result event: {event_id_hex}")
                        await self._process_result_event(ev)
                        logger.info(f"Job completed with result event: {event_id_hex}")
                        self.job_completed.set()
                    elif (
                        event_kind >= 6000 and event_kind < 7000
                    ):  # Other job result events
                        logger.info(
                            f"Received kind {event_kind} result event: {event_id_hex}"
                        )
                        await self._process_result_event(ev)
                        # Only set job_completed for kind 6109
                        if event_kind == 6109:
                            logger.info(
                                f"Job completed with result event: {event_id_hex}"
                            )
                            self.job_completed.set()

                    break

    async def handle_msg(self, relay_url, msg):
        if msg.as_enum().is_end_of_stored_events():
            logger.info(f"Received EOSE from {relay_url}")

    async def _process_offer_event(self, event):
        """Process a job offer event (kind 7000)"""
        # Extract price and invoice from tags
        price = None
        invoice = None
        status = None

        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2:
                if tag_vec[0] == "amount":
                    try:
                        price = int(tag_vec[1])
                    except ValueError:
                        pass
                elif tag_vec[0] == "bolt11":
                    invoice = tag_vec[1]
                elif tag_vec[0] == "status":
                    status = tag_vec[1]

        # Log the offer details
        logger.info(
            f"Offer details - Price: {price} sats, Status: {status}, Invoice: {'Present' if invoice else 'Not present'}"
        )

        # Store the offer
        offer_data = {
            "event_id": event.id().to_hex(),
            "price_sats": price,
            "invoice": invoice,
            "status": status,
            "pubkey": event.author().to_hex(),
            "content": event.content(),
            "received_at": time.time(),
        }

        self.offers.append(offer_data)
        logger.info(f"Added offer to list. Total offers: {len(self.offers)}")

        # Pay the invoice if it exists and price is within limits
        if invoice and price is not None:
            try:
                logger.info(
                    f"Attempting to pay invoice for offer {event.id().to_hex()}"
                )
                payment_result = await pay_lightning_invoice(
                    invoice=invoice,
                    price_sats=price,
                    note=f"Payment for Nostr event {self.event_id}",
                )

                # Update the offer with payment information
                offer_data["payment_result"] = payment_result
                logger.info(f"Payment successful for offer {event.id().to_hex()}")

            except Exception as e:
                logger.error(
                    f"Failed to pay invoice for offer {event.id().to_hex()}: {str(e)}"
                )
                offer_data["payment_error"] = str(e)

    async def _process_result_event(self, event):
        """Process a job result event (kind 6xxx)"""
        event_id = event.id().to_hex()
        event_kind = event.kind().as_u16()

        # Extract status from tags
        status = None
        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "status":
                status = tag_vec[1]
                break

        # Log the result details
        logger.info(
            f"Result event received - ID: {event_id}, Kind: {event_kind}, Status: {status}"
        )

        content_json = None
        try:
            # Try to parse content as JSON
            content_json = json.loads(event.content())
            logger.info(
                f"Result content (JSON): {json.dumps(content_json, indent=2)[:200]}..."
            )
        except json.JSONDecodeError:
            # If not JSON, log as text
            logger.info(f"Result content (text): {event.content()[:200]}...")

        # Check if this is a kind 6109 event with actions to execute
        if event_kind == 6109 and content_json and PYAUTOGUI_AVAILABLE:
            try:
                logger.info("Detected kind 6109 event with potential actions")

                # Check if the content has the expected format for actions
                if (
                    isinstance(content_json, dict)
                    and "actions" in content_json
                    and isinstance(content_json["actions"], list)
                ):

                    logger.info(
                        f"Found {len(content_json['actions'])} actions to execute"
                    )

                    # Execute the actions
                    execution_result = execute_actions(content_json)

                    logger.info(
                        f"Actions execution result: {json.dumps(execution_result)}"
                    )

                    # Add the execution result to the content
                    content_json["execution_result"] = execution_result

                    # Update the event content with the execution result
                    event_content = json.dumps(content_json)
                else:
                    logger.info("Kind 6109 event does not contain valid actions format")
            except Exception as e:
                logger.error(f"Error executing actions from kind 6109 event: {str(e)}")
                # If there's an error, add it to the content
                if content_json:
                    content_json["execution_error"] = str(e)
                    event_content = json.dumps(content_json)
                else:
                    event_content = event.content()
        else:
            # Use the original content
            event_content = event.content()

        # Store the result
        self.result = {
            "event_id": event_id,
            "kind": event_kind,
            "pubkey": event.author().to_hex(),
            "content": event_content,
            "status": status,
            "tags": [tag.as_vec() for tag in event.tags().to_vec()],
            "received_at": time.time(),
        }

        logger.info(f"Stored result for event: {event_id}")


# Function to pay a Lightning invoice using NWC
async def pay_lightning_invoice_nwc(
    invoice: str, price_sats: Optional[int] = None, note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Pay a BOLT11 Lightning invoice using Nostr Wallet Connect (NWC).

    Args:
        invoice: The encoded invoice string to pay
        price_sats: The price in satoshis (for validation)
        note: Optional personal note to attach to the payment

    Returns:
        Dictionary containing the payment result
    """
    if not NOSTR_SDK_AVAILABLE or not nwc:
        logger.error("NWC client not available")
        raise McpError(ErrorData(INTERNAL_ERROR, "NWC client not available"))

    try:
        # Check if price is within limits
        if price_sats and price_sats > MAX_AUTO_PAYMENT_SATS:
            logger.warning(
                f"Invoice price ({price_sats} sats) exceeds maximum auto-payment limit ({MAX_AUTO_PAYMENT_SATS} sats)"
            )
            raise McpError(
                ErrorData(
                    INVALID_PARAMS,
                    f"Invoice price ({price_sats} sats) exceeds maximum auto-payment limit",
                )
            )

        logger.info(
            f"Preparing to pay Lightning invoice via NWC (price: {price_sats if price_sats else 'unknown'} sats)"
        )

        # Create payment request parameters
        # Note: For PayInvoiceRequest, we don't need to specify amount as it's included in the invoice
        # But if we did, it might need to be in millisatoshis (msats) instead of satoshis
        params = PayInvoiceRequest(invoice=invoice, id=None, amount=None)

        # Pay the invoice using NWC
        logger.info("Sending payment request via NWC")
        try:
            payment_result = await nwc.pay_invoice(params)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"NWC payment error: {error_msg}")

            # Add more detailed error information
            if "Only sat payments are supported" in error_msg:
                logger.error(
                    "This error suggests the wallet only supports payments in satoshis."
                )
                logger.error(
                    "Check if your NWC wallet implementation has specific requirements for payments."
                )

        return result

    except Exception as e:
        logger.error(f"Error paying Lightning invoice via NWC: {str(e)}")
        raise McpError(
            ErrorData(
                INTERNAL_ERROR, f"Error paying Lightning invoice via NWC: {str(e)}"
            )
        )


# Function to pay a Lightning invoice
async def pay_lightning_invoice(
    invoice: str, price_sats: Optional[int] = None, note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Pay a BOLT11 Lightning invoice using either NWC or the Lexe node API.
    Tries NWC first, falls back to Lexe if NWC fails.

    Args:
        invoice: The encoded invoice string to pay
        price_sats: The price in satoshis (for validation)
        note: Optional personal note to attach to the payment

    Returns:
        Dictionary containing the payment index and creation timestamp
    """
    # Check if price is within limits
    if price_sats and price_sats > MAX_AUTO_PAYMENT_SATS:
        logger.warning(
            f"Invoice price ({price_sats} sats) exceeds maximum auto-payment limit ({MAX_AUTO_PAYMENT_SATS} sats)"
        )
        raise McpError(
            ErrorData(
                INVALID_PARAMS,
                f"Invoice price ({price_sats} sats) exceeds maximum auto-payment limit",
            )
        )

    logger.info(
        f"Preparing to pay Lightning invoice (price: {price_sats if price_sats else 'unknown'} sats)"
    )

    # Try to pay with NWC first if available
    if NOSTR_SDK_AVAILABLE and nwc:
        try:
            logger.info("Attempting to pay with NWC")
            return await pay_lightning_invoice_nwc(invoice, price_sats, note)
        except Exception as e:
            logger.warning(f"NWC payment failed, falling back to Lexe: {str(e)}")
            # Fall back to Lexe if NWC fails

    # Pay with Lexe API
    try:
        logger.info("Attempting to pay with Lexe API")

        # Prepare the request payload
        payload = {"invoice": invoice}

        # Add optional note if provided
        if note:
            payload["note"] = note

        logger.info(
            f"Sending payment request to {LEXE_PROXY_NODE_API_URL}/v1/node/pay_invoice"
        )

        # Make the API request
        response = requests.post(
            f"{LEXE_PROXY_NODE_API_URL}/v1/node/pay_invoice",
            headers={"content-type": "application/json"},
            json=payload,
        )

        # Check if the request was successful
        response.raise_for_status()

        # Parse and return the response
        result = response.json()
        logger.info(
            f"Successfully paid invoice via Lexe. Payment index: {result.get('index')}"
        )
        logger.info(f"Payment created at: {result.get('created_at')}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error paying Lightning invoice via Lexe: {str(e)}")
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Error paying Lightning invoice: {str(e)}")
        )


# Function to check if a string is a local file path and upload it if needed
def ensure_public_url(file_path_or_url: str) -> str:
    """
    Check if the provided string is a local file path.
    If it is, upload it to Digital Ocean Spaces and return the public URL.
    Otherwise, return the original URL.

    Args:
        file_path_or_url: A string that could be either a local file path or a URL

    Returns:
        A public URL (either the original URL or a new one if the file was uploaded)
    """
    # Check if it's a local file path
    if os.path.exists(file_path_or_url) and os.path.isfile(file_path_or_url):
        logger.info(f"Detected local file path: {file_path_or_url}")

        # Generate a unique remote path
        remote_path = (
            f"uploads/screenshot_{int(time.time())}_{random.randint(1,10000)}.png"
        )

        # Upload the file
        logger.info(
            f"Uploading to Digital Ocean Spaces: {file_path_or_url} -> {remote_path}"
        )
        success = upload_to_space(file_path_or_url, remote_path)

        if success:
            # Generate and return the public URL
            public_url = f"https://{DIGITAL_OCEAN_SPACE_NAME}.{DIGITAL_OCEAN_REGION}.digitaloceanspaces.com/{remote_path}"
            logger.info(f"Successfully uploaded to Digital Ocean Spaces: {public_url}")
            return public_url
        else:
            logger.error(f"Failed to upload local file: {file_path_or_url}")
            # Return original path if upload fails
            return file_path_or_url

    # If it's not a local file or upload fails, return the original URL
    return file_path_or_url


# Initialize Nostr client
async def init_nostr_client():
    """Initialize connection to Nostr relays"""
    if not NOSTR_SDK_AVAILABLE:
        return

    for relay_url in RELAY_URLS:
        await client.add_relay(relay_url.strip())
    await client.connect()


# Function to send a request and wait for result
async def request_and_wait_for_result(
    description, screenshot_url, max_price_sats=None, timeout=300
):
    """
    Send a request for visual computer interaction help and wait for the result.
    """
    try:
        if not NOSTR_SDK_AVAILABLE:
            logger.warning("Nostr SDK not available, returning mock response")
            return {
                "job_id": "mock-job-id",
                "offers": [],
                "selected_offer": None,
                "result": {
                    "content": f"Mock response for: {description} (Nostr SDK not available)",
                    "screenshot_url": screenshot_url,
                    "max_price_sats": max_price_sats,
                },
            }

        # Create and broadcast the event
        try:
            logger.info("Creating and broadcasting Nostr event")
            broadcast_result = await create_and_broadcast_nostr_event(
                description, screenshot_url, max_price_sats
            )
            job_id = broadcast_result["event_id"]
            logger.info(f"Sent job request with ID: {job_id}")
        except Exception as e:
            logger.error(
                f"Failed to create and broadcast Nostr event: {str(e)}", exc_info=True
            )
            return {
                "error": str(e),
                "status": "failed",
                "job_id": "error-" + str(int(time.time())),
                "offers": [],
                "selected_offer": None,
                "result": {
                    "content": f"Error creating Nostr event: {str(e)}",
                    "error": str(e),
                },
            }

        # Create notification handler for this job
        handler = NotificationHandler(job_id)

        # Set up filter for responses to our event
        one_hour_ago = Timestamp.from_secs(Timestamp.now().as_secs() - 3600)

        # Create a filter for events that reference our event ID
        response_filter = (
            Filter()
            .event(EventId.parse(job_id))  # Filter for events referencing our event ID
            .since(one_hour_ago)
        )

        logger.info(f"Setting up filter for events referencing job ID: {job_id}")

        try:
            await client.subscribe(response_filter)
            logger.info(f"Successfully subscribed to filter for job ID: {job_id}")
        except Exception as e:
            logger.error(f"Failed to subscribe to filter: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed",
                "job_id": job_id,
                "offers": [],
                "selected_offer": None,
                "result": {
                    "content": f"Error subscribing to filter: {str(e)}",
                    "error": str(e),
                },
                "broadcast_info": {
                    "sent_to": broadcast_result["success"],
                    "failed_relays": broadcast_result["failed"],
                },
            }

        # Start handling notifications
        notification_task = asyncio.create_task(client.handle_notifications(handler))

        try:
            # Wait for job completion or timeout
            logger.info(f"Waiting for job completion (timeout: {timeout}s)")
            await asyncio.wait_for(handler.job_completed.wait(), timeout=timeout)
            logger.info(f"Job {job_id} completed")
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for job {job_id} to complete")
            # Return a timeout result
            return {
                "job_id": job_id,
                "offers": handler.offers,
                "selected_offer": None,
                "result": {
                    "content": f"Timeout waiting for response after {timeout} seconds",
                    "status": "timeout",
                    "error": "Request timed out",
                },
                "broadcast_info": {
                    "sent_to": broadcast_result["success"],
                    "failed_relays": broadcast_result["failed"],
                },
                "status": "timeout",
            }
        except Exception as e:
            logger.error(f"Error waiting for job completion: {str(e)}", exc_info=True)
            # Return an error result
            return {
                "error": str(e),
                "status": "failed",
                "job_id": job_id,
                "offers": handler.offers,
                "selected_offer": None,
                "result": {
                    "content": f"Error waiting for job completion: {str(e)}",
                    "error": str(e),
                },
                "broadcast_info": {
                    "sent_to": broadcast_result["success"],
                    "failed_relays": broadcast_result["failed"],
                },
            }
        finally:
            # Cancel notification handling
            logger.info("Canceling notification handling task")
            notification_task.cancel()
            try:
                await notification_task
            except asyncio.CancelledError:
                pass

        # Return the job result
        logger.info(f"Returning job result for job ID: {job_id}")
        return {
            "job_id": job_id,
            "offers": handler.offers,
            "selected_offer": None,
            "result": handler.result
            or {"content": "No result received", "status": "no_result"},
            "broadcast_info": {
                "sent_to": broadcast_result["success"],
                "failed_relays": broadcast_result["failed"],
            },
        }
    except Exception as e:
        logger.error(
            f"Unexpected error in request_and_wait_for_result: {str(e)}", exc_info=True
        )
        # Always return a result, even on unexpected errors
        return {
            "error": str(e),
            "status": "failed",
            "job_id": "error-" + str(int(time.time())),
            "offers": [],
            "selected_offer": None,
            "result": {
                "content": f"Unexpected error in request_and_wait_for_result: {str(e)}",
                "error": str(e),
            },
        }


# Function to create and broadcast a Nostr event
async def create_and_broadcast_nostr_event(
    description: str, screenshot_url: str, max_price_sats: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create and broadcast a Nostr event requesting visual help.

    Args:
        description: A detailed description of what help is needed
        screenshot_url: URL to a screenshot or image showing the visual context
        max_price_sats: Maximum price willing to pay in satoshis (optional)

    Returns:
        Dictionary containing event ID and broadcast results
    """
    try:
        if not NOSTR_SDK_AVAILABLE:
            logger.warning("Nostr SDK not available, cannot create event")
            return {"event_id": "mock-event-id", "success": [], "failed": []}

        # Create kind 5109 event for help request
        logger.info("Creating Nostr event tags")
        try:
            tags = [
                Tag.parse(["description", description]),
                Tag.parse(["image", screenshot_url]),
            ]

            if max_price_sats:
                tags.append(Tag.parse(["max_price", str(max_price_sats)]))
        except Exception as e:
            logger.error(f"Error creating tags: {str(e)}", exc_info=True)
            raise

        # Build the event
        logger.info("Building Nostr event")
        try:
            builder = EventBuilder(Kind(5109), description).tags(tags)
        except Exception as e:
            logger.error(f"Error building event: {str(e)}", exc_info=True)
            raise

        # Add relays and connect
        logger.info("Connecting to relays")
        try:
            for relay_url in RELAY_URLS:
                await client.add_relay(relay_url.strip())
            await client.connect()
            logger.info(f"Connected to relays: {RELAY_URLS}")
        except Exception as e:
            logger.error(f"Error connecting to relays: {str(e)}", exc_info=True)
            raise

        # Send the event to relays
        logger.info("Sending event to relays")
        try:
            output = await client.send_event_builder(builder)
            event_id = output.id.to_hex()

            logger.info(f"Event ID: {event_id}")
            logger.info(f"Sent to: {output.success}")
            logger.info(f"Not sent to: {output.failed}")

            return {
                "event_id": event_id,
                "success": output.success,
                "failed": output.failed,
            }
        except Exception as e:
            logger.error(f"Error sending event to relays: {str(e)}", exc_info=True)
            raise

    except Exception as e:
        logger.error(
            f"Error in create_and_broadcast_nostr_event: {str(e)}", exc_info=True
        )
        # Generate a mock event ID for error cases
        mock_event_id = f"error-{int(time.time())}"
        return {
            "event_id": mock_event_id,
            "success": [],
            "failed": RELAY_URLS,
            "error": str(e),
        }


@mcp.tool()
async def request_visual_help(
    description: str = "",
    screenshot_url: str = "",
    max_price_sats: Optional[int] = None,
    wait_for_result: bool = True,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Request visual computer interaction help from humans through Nostr.

    This tool sends a request to Nostr relays asking for help with a visual computer interaction task.
    It broadcasts the request to all configured relays and waits for responses.

    Args:
        description: A detailed description of what help is needed
        screenshot_url: URL to a screenshot or image showing the visual context (can be a local file path)
        max_price_sats: Maximum price willing to pay in satoshis (optional)
        wait_for_result: Whether to wait for the result (default: True)
        timeout: Maximum time to wait for result in seconds (default: 300)

    Returns:
        A dictionary containing the job ID, offers received, selected offer, and result
    """
    try:
        # Enhanced logging for tool calls from Goose
        logger.info("==== TOOL CALL FROM GOOSE ====")
        logger.info(f"Description: {description}")
        logger.info(f"Screenshot URL: {screenshot_url}")
        logger.info(f"Max price: {max_price_sats}")
        logger.info(f"Wait for result: {wait_for_result}")
        logger.info(f"Timeout: {timeout}s")
        logger.info("================================")

        # Log raw arguments in debug mode
        if DEBUG_MODE:
            logger.info("==== RAW ARGUMENTS ====")
            import inspect

            frame = inspect.currentframe()
            args, _, _, values = inspect.getargvalues(frame)
            for arg in args:
                if arg != "self":
                    logger.info(f"{arg}: {values[arg]}")
            logger.info("=======================")

        # Check if screenshot_url is a local file path and upload if needed
        public_url = ""
        if screenshot_url:
            logger.info(f"Processing screenshot URL: {screenshot_url}")
            try:
                public_url = ensure_public_url(screenshot_url)
                if public_url == screenshot_url and not public_url.startswith(
                    ("http://", "https://")
                ):
                    # If the URL didn't change and it's not a web URL, it means upload failed
                    logger.error(f"Failed to upload local screenshot: {screenshot_url}")
                    return {
                        "error": "Screenshot upload failed",
                        "status": "failed",
                        "job_id": "error-" + str(int(time.time())),
                        "offers": [],
                        "selected_offer": None,
                        "result": {
                            "content": f"Error: Failed to upload local screenshot: {screenshot_url}",
                            "error": "Screenshot upload failed",
                        },
                    }
                logger.info(f"Successfully processed to: {public_url}")
            except Exception as e:
                logger.error(
                    f"Failed to process screenshot URL: {str(e)}", exc_info=True
                )
                return {
                    "error": str(e),
                    "status": "failed",
                    "job_id": "error-" + str(int(time.time())),
                    "offers": [],
                    "selected_offer": None,
                    "result": {
                        "content": f"Error processing screenshot URL: {str(e)}",
                        "error": str(e),
                    },
                }
        else:
            logger.warning("No screenshot URL provided")
            # If screenshot is required, return an error
            if not description:
                logger.error("Neither screenshot URL nor description provided")
                return {
                    "error": "Missing required parameters",
                    "status": "failed",
                    "job_id": "error-" + str(int(time.time())),
                    "offers": [],
                    "selected_offer": None,
                    "result": {
                        "content": "Error: Neither screenshot URL nor description provided",
                        "error": "Missing required parameters",
                    },
                }

        if wait_for_result:
            # Use the request_and_wait_for_result function to wait for responses
            logger.info("Waiting for result...")
            result = await request_and_wait_for_result(
                description, public_url, max_price_sats, timeout
            )
            logger.info(f"Received result after waiting: {result}")
            return result
        else:
            # Just broadcast the event without waiting
            logger.info("Broadcasting event without waiting for result")
            broadcast_result = await create_and_broadcast_nostr_event(
                description, public_url, max_price_sats
            )

            event_id = broadcast_result["event_id"]
            logger.info(f"Broadcast Nostr event with ID: {event_id}")
            logger.info(f"Successfully sent to: {broadcast_result['success']}")

            if broadcast_result["failed"]:
                logger.warning(f"Failed to send to: {broadcast_result['failed']}")

            # Return a response with the event ID and broadcast results
            result = {
                "job_id": event_id,
                "offers": [],
                "selected_offer": None,
                "result": {
                    "content": f"Broadcast request for: {description}",
                    "screenshot_url": public_url,
                    "original_screenshot_path": (
                        screenshot_url if public_url != screenshot_url else None
                    ),
                    "max_price_sats": max_price_sats,
                    "event_id": event_id,
                    "sent_to": broadcast_result["success"],
                    "failed_relays": broadcast_result["failed"],
                },
            }

            logger.info(f"Returning immediate result: {result}")
            return result
    except Exception as e:
        logger.error(f"Error requesting visual help: {str(e)}", exc_info=True)
        # Always return a result, even on error
        return {
            "error": str(e),
            "status": "failed",
            "job_id": "error-" + str(int(time.time())),
            "offers": [],
            "selected_offer": None,
            "result": {
                "content": f"Error in request_visual_help: {str(e)}",
                "error": str(e),
            },
        }


if __name__ == "__main__":
    mcp.run()
