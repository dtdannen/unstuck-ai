#!/usr/bin/env python3
import os
import asyncio
import json
from typing import Dict, Set
from dotenv import load_dotenv
from nostr_sdk import (
    Keys,
    Client,
    NostrSigner,
    Kind,
    Filter,
    Event,
    HandleNotification,
    RelayMessage,
    Timestamp,
)

# Load environment variables
load_dotenv()

# Get environment variables
RELAY_URLS = os.getenv(
    "RELAY_URLS",
    "wss://relay.damus.io,wss://relay.supertech.ai,wss://relay.primal.net,wss://relay.dvmdash.live",
).split(",")


class EventMonitor(HandleNotification):
    """Handler for Nostr notifications."""

    def __init__(self):
        self.request_events: Dict[str, dict] = {}  # Store request events by ID
        self.seen_events: Set[str] = set()  # Track seen events to avoid duplicates

    async def handle(self, relay_url: str, subscription_id: str, ev: Event):
        event_id_hex = ev.id().to_hex()

        # Skip if we've already seen this event
        if event_id_hex in self.seen_events:
            return

        self.seen_events.add(event_id_hex)
        event_kind = ev.kind().as_u16()

        # Process based on event kind
        if event_kind == 5109:  # Request event
            await self._process_request_event(relay_url, ev)
        elif event_kind == 7000:  # Offer event
            await self._process_offer_event(relay_url, ev)
        elif event_kind == 6109 or (
            event_kind >= 6000 and event_kind < 7000
        ):  # Result event
            await self._process_result_event(relay_url, ev)

    async def handle_msg(self, relay_url: str, msg: RelayMessage):
        if msg.as_enum().is_end_of_stored_events():
            print(f"Received EOSE from {relay_url}")

    async def _process_request_event(self, relay_url: str, event: Event):
        """Process a request event (kind 5109)"""
        event_id = event.id().to_hex()

        # Extract description from tags
        description = event.content()
        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "description":
                description = tag_vec[1]
                break

        # Store request event
        self.request_events[event_id] = {
            "description": description,
            "pubkey": event.author().to_hex(),
            "created_at": event.created_at().as_secs(),
        }

        print(
            f"REQUEST: {event_id[:8]}... - {description[:50]}{'...' if len(description) > 50 else ''}"
        )

    async def _process_offer_event(self, relay_url: str, event: Event):
        """Process an offer event (kind 7000)"""
        # Check if this event references any of our tracked request events
        referenced_request = None

        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "e":
                request_id = tag_vec[1]
                if request_id in self.request_events:
                    referenced_request = request_id
                    break

        if referenced_request:
            # Extract price and invoice from tags
            price = "unknown"
            invoice = None

            for tag in event.tags().to_vec():
                tag_vec = tag.as_vec()
                if len(tag_vec) >= 2:
                    if tag_vec[0] == "amount":
                        try:
                            price = tag_vec[1]
                        except (ValueError, IndexError):
                            pass
                    elif tag_vec[0] == "bolt11":
                        invoice = tag_vec[1]

            request_desc = self.request_events[referenced_request]["description"]
            print(
                f"OFFER for {referenced_request[:8]}... - Price: {price} sats - {event.content()[:30]}{'...' if len(event.content()) > 30 else ''}"
            )

    async def _process_result_event(self, relay_url: str, event: Event):
        """Process a result event (kind 6xxx)"""
        # Check if this event references any of our tracked request events
        referenced_request = None

        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "e":
                request_id = tag_vec[1]
                if request_id in self.request_events:
                    referenced_request = request_id
                    break

        if referenced_request:
            request_desc = self.request_events[referenced_request]["description"]
            print(
                f"RESULT for {referenced_request[:8]}... - Kind: {event.kind().as_u16()} - {event.content()[:30]}{'...' if len(event.content()) > 30 else ''}"
            )


async def main():
    """Main function to run the event monitor."""
    print("Starting Nostr Event Monitor for MCP Server")
    print(f"Connecting to relays: {', '.join(RELAY_URLS)}")

    # Generate temporary keys for the monitor
    keys = Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)

    # Connect to relays
    for relay_url in RELAY_URLS:
        await client.add_relay(relay_url.strip())
    await client.connect()

    print(f"Connected to relays with public key: {keys.public_key().to_bech32()}")

    # Create notification handler
    handler = EventMonitor()

    # Set up filter for events
    # Get events from the last hour
    one_hour_ago = Timestamp.from_secs(Timestamp.now().as_secs() - 3600)

    # Create filter for kinds 5109, 7000, and 6109
    event_filter = (
        Filter().kinds([Kind(5109), Kind(7000), Kind(6109)]).since(one_hour_ago)
    )

    # Subscribe to events
    await client.subscribe(event_filter)

    print("Subscribed to events. Monitoring for events...")
    print("Press Ctrl+C to stop")

    try:
        # Start handling notifications
        await client.handle_notifications(handler)
    except KeyboardInterrupt:
        print("\nStopping event monitor...")
    finally:
        # Disconnect from relays
        await client.disconnect()
        print("Disconnected from relays")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEvent monitor stopped")
