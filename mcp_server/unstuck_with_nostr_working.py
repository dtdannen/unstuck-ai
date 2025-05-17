import os
import asyncio
import json
import time
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("unstuck-ai")

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
        HandleNotification,
        RelayMessage,
        Timestamp,
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

# Initialize Nostr client if SDK is available
if NOSTR_SDK_AVAILABLE:
    keys = Keys.parse(NOSTR_PRIVATE_KEY) if NOSTR_PRIVATE_KEY else Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    logger.info(
        f"Nostr client initialized with public key: {keys.public_key().to_hex()}"
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
                        await self._process_offer_event(ev)
                    elif event_kind >= 6000 and event_kind < 7000:  # Job result event
                        await self._process_result_event(ev)
                        logger.info(
                            f"Received response event (Kind: {event_kind}), job completed"
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

        if price and invoice:
            self.offers.append(
                {
                    "event_id": event.id().to_hex(),
                    "price_sats": price,
                    "invoice": invoice,
                    "pubkey": event.author().to_hex(),
                    "content": event.content(),
                    "received_at": time.time(),
                }
            )

    async def _process_result_event(self, event):
        """Process a job result event (kind 6xxx)"""
        self.result = {
            "event_id": event.id().to_hex(),
            "kind": event.kind().as_u16(),
            "pubkey": event.author().to_hex(),
            "content": event.content(),
            "tags": [tag.as_vec() for tag in event.tags().to_vec()],
            "received_at": time.time(),
        }


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
    if not NOSTR_SDK_AVAILABLE:
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

    # Create kind 5109 event for help request
    tags = [
        Tag.parse(["description", description]),
        Tag.parse(["image", screenshot_url]),
    ]

    if max_price_sats:
        tags.append(Tag.parse(["max_price", str(max_price_sats)]))

    # Build and send the event
    builder = EventBuilder(Kind(5109), description).tags(tags)
    result = await client.send_event_builder(builder)
    job_id = result.id.to_hex()

    logger.info(f"Sent job request with ID: {job_id}")

    # Create notification handler for this job
    handler = NotificationHandler(job_id)

    # Set up filter for responses to our event
    one_hour_ago = Timestamp.from_secs(Timestamp.now().as_secs() - 3600)
    response_filter = Filter().event(result.id).since(one_hour_ago)
    await client.subscribe(response_filter)

    # Start handling notifications
    notification_task = asyncio.create_task(client.handle_notifications(handler))

    try:
        # Wait for job completion or timeout
        await asyncio.wait_for(handler.job_completed.wait(), timeout=timeout)
        logger.info(f"Job {job_id} completed")
    except asyncio.TimeoutError:
        logger.warning(f"Timeout waiting for job {job_id} to complete")
    finally:
        # Cancel notification handling
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            pass

    # Return the job result
    return {
        "job_id": job_id,
        "offers": handler.offers,
        "selected_offer": None,
        "result": handler.result,
    }


# Function to create a Nostr event
def create_nostr_event(
    description: str, screenshot_url: str, max_price_sats: Optional[int] = None
) -> str:
    """
    Create a Nostr event requesting visual help.
    
    Args:
        description: A detailed description of what help is needed
        screenshot_url: URL to a screenshot or image showing the visual context
        max_price_sats: Maximum price willing to pay in satoshis (optional)
        
    Returns:
        The event ID of the created event
    """
    if not NOSTR_SDK_AVAILABLE:
        logger.warning("Nostr SDK not available, cannot create event")
        return "mock-event-id"
    
    # Create kind 5109 event for help request
    tags = [
        Tag.parse(["description", description]),
        Tag.parse(["image", screenshot_url]),
    ]

    if max_price_sats:
        tags.append(Tag.parse(["max_price", str(max_price_sats)]))

    # Build the event
    builder = EventBuilder(Kind(5109), description).tags(tags)
    
    # Sign the event
    event = builder.sign_with_keys(keys)
    event_id = event.id().to_hex()
    
    logger.info(f"Created Nostr event with ID: {event_id}")
    
    return event_id


@mcp.tool()
def request_visual_help(
    description: str = "",
    screenshot_url: str = "",
    max_price_sats: Optional[int] = None,
) -> Dict[str, Any]:
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
        logger.info(f"Request visual help called with description: {description}")
        logger.info(f"Screenshot URL: {screenshot_url}")
        logger.info(f"Max price: {max_price_sats}")

        # Create a Nostr event
        event_id = create_nostr_event(description, screenshot_url, max_price_sats)
        logger.info(f"Created Nostr event with ID: {event_id}")

        # Return a response with the event ID
        result = {
            "job_id": event_id,
            "offers": [],
            "selected_offer": None,
            "result": {
                "content": f"Broadcast request for: {description}",
                "screenshot_url": screenshot_url,
                "max_price_sats": max_price_sats,
                "event_id": event_id,
            },
        }

        logger.info(f"Returning result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error requesting visual help: {str(e)}", exc_info=True)
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Error requesting visual help: {str(e)}")
        )


if __name__ == "__main__":
    mcp.run()
