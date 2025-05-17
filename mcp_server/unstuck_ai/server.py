import os
import asyncio
import json
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

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

# Initialize Nostr client
keys = Keys.parse(NOSTR_PRIVATE_KEY) if NOSTR_PRIVATE_KEY else Keys.generate()
signer = NostrSigner.keys(keys)
client = Client(signer)

# Initialize FastAPI app for internal use
app = FastAPI(title="MCP Server")


class VisualHelpRequest(BaseModel):
    description: str
    screenshot_url: str
    max_price_sats: Optional[int] = None


class JobResult(BaseModel):
    job_id: str
    offers: List[Dict[str, Any]]
    selected_offer: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


class NotificationHandler(HandleNotification):
    """Handler for Nostr notifications."""

    def __init__(self, event_id: str):
        self.event_id = event_id
        self.job_completed = asyncio.Event()
        self.offers = []
        self.result = None

    async def handle(self, relay_url: str, subscription_id: str, ev: Event):
        event_id_hex = ev.id().to_hex()
        event_kind = ev.kind().as_u16()

        # Check if this event references our request
        is_related = False
        for tag in ev.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "e":
                if tag_vec[1] == self.event_id:
                    is_related = True
                    print(f"Found related event: {event_id_hex} (Kind: {event_kind})")

                    # Process the event based on its kind
                    if event_kind == 7000:  # Job response event (offer)
                        await self._process_offer_event(ev)
                    elif event_kind >= 6000 and event_kind < 7000:  # Job result event
                        await self._process_result_event(ev)
                        print(
                            f"Received response event (Kind: {event_kind}), job completed"
                        )
                        self.job_completed.set()

                    break

        if not is_related:
            # Check for other ways it might be related
            for tag in ev.tags().to_vec():
                tag_vec = tag.as_vec()
                if len(tag_vec) >= 2 and tag_vec[0] == "request":
                    try:
                        request_data = json.loads(tag_vec[1])
                        if request_data.get("id") == self.event_id:
                            is_related = True
                            print(
                                f"Found related event via 'request' tag: {event_id_hex}"
                            )

                            # Process the event based on its kind
                            if event_kind == 7000:  # Job response event (offer)
                                await self._process_offer_event(ev)
                            elif (
                                event_kind >= 6000 and event_kind < 7000
                            ):  # Job result event
                                await self._process_result_event(ev)
                                print(
                                    f"Received response event (Kind: {event_kind}), job completed"
                                )
                                self.job_completed.set()

                            break
                    except (json.JSONDecodeError, KeyError):
                        pass

    async def handle_msg(self, relay_url: str, msg: RelayMessage):
        if msg.as_enum().is_end_of_stored_events():
            print(f"Received EOSE from {relay_url}")

    async def _process_offer_event(self, event: Event):
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

    async def _process_result_event(self, event: Event):
        """Process a job result event (kind 6xxx)"""
        self.result = {
            "event_id": event.id().to_hex(),
            "kind": event.kind().as_u16(),
            "pubkey": event.author().to_hex(),
            "content": event.content(),
            "tags": [tag.as_vec() for tag in event.tags().to_vec()],
            "received_at": time.time(),
        }


async def init_nostr_client():
    """Initialize connection to Nostr relays"""
    for relay_url in RELAY_URLS:
        await client.add_relay(relay_url.strip())
    await client.connect()


async def request_and_wait_for_result(
    request: VisualHelpRequest, timeout: int = 300
) -> JobResult:
    """
    Send a request for visual computer interaction help and wait for the result.

    Args:
        request: The visual help request details
        timeout: Maximum time to wait for a result in seconds

    Returns:
        JobResult object containing offers and result
    """
    # Create kind 5109 event for help request
    tags = [
        Tag.parse(["description", request.description]),
        Tag.parse(["image", request.screenshot_url]),
    ]

    if request.max_price_sats:
        tags.append(Tag.parse(["max_price", str(request.max_price_sats)]))

    # Build and send the event
    builder = EventBuilder(Kind(5109), request.description).tags(tags)
    result = await client.send_event_builder(builder)
    job_id = result.id.to_hex()

    print(f"Sent job request with ID: {job_id}")

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
        print(f"Job {job_id} completed")
    except asyncio.TimeoutError:
        print(f"Timeout waiting for job {job_id} to complete")
    finally:
        # Cancel notification handling
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            pass

    # If we have offers but no result, automatically select the cheapest offer
    if handler.offers and not handler.result and request.max_price_sats:
        valid_offers = [
            offer
            for offer in handler.offers
            if offer["price_sats"] <= request.max_price_sats
        ]

        if valid_offers:
            # Sort by price and select the cheapest
            cheapest_offer = min(valid_offers, key=lambda x: x["price_sats"])

            # Here you would integrate with a Lightning wallet to pay the invoice
            # For now, we'll just mark it as selected
            selected_offer = cheapest_offer

            # TODO: Implement payment and wait for result
            # This would involve paying the invoice and waiting for the result event

            return JobResult(job_id=job_id, offers=handler.offers, selected_offer=selected_offer, result=handler.result)

    # Return the job result
    return JobResult(job_id=job_id, offers=handler.offers, selected_offer=None, result=handler.result)


@app.on_event("startup")
async def startup_event():
    """Initialize Nostr client on startup"""
    await init_nostr_client()


@mcp.tool()
async def request_visual_help(
    description: str = "", screenshot_url: str = "", max_price_sats: Optional[int] = None
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
        # Initialize Nostr client if not already connected
        if not client.is_connected():
            await init_nostr_client()

        # Create the request
        request = VisualHelpRequest(description=description, screenshot_url=screenshot_url, max_price_sats=max_price_sats)

        # Send the request and wait for result
        result = await request_and_wait_for_result(request)

        # Return the result as a dictionary
        return {
            "job_id": result.job_id,
            "offers": result.offers,
            "selected_offer": result.selected_offer,
            "result": result.result,
        }
    except Exception as e:
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Error requesting visual help: {str(e)}")
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
