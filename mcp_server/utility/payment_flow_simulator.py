#!/usr/bin/env python3
import os
import asyncio
import json
import time
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
    Tag,
    EventBuilder,
    NostrWalletConnectUri,
    Nwc,
    MakeInvoiceRequest,
    LookupInvoiceRequest,
)

# Load environment variables
load_dotenv()

# Get environment variables
RELAY_URLS = os.getenv(
    "RELAY_URLS",
    "wss://relay.damus.io,wss://relay.supertech.ai,wss://relay.primal.net,wss://relay.dvmdash.live",
).split(",")
NWC_KEY = os.getenv("NWC_KEY_PAYMENT_FLOW")


class PaymentFlowSimulator(HandleNotification):
    """Handler for Nostr notifications that simulates the payment flow."""

    def __init__(self, client, keys):
        self.client = client
        self.keys = keys
        self.request_events: Dict[str, dict] = {}  # Store request events by ID
        self.seen_events: Set[str] = set()  # Track seen events to avoid duplicates
        self.processing_events: Set[str] = set()  # Track events being processed

        # Initialize NWC client
        if NWC_KEY:
            uri = NostrWalletConnectUri.parse(NWC_KEY)
            self.nwc = Nwc(uri)
        else:
            self.nwc = None
            print(
                "Warning: NWC_KEY not found in environment variables. Invoice creation will be simulated."
            )

    async def handle(self, relay_url: str, subscription_id: str, ev: Event):
        event_id_hex = ev.id().to_hex()

        # Skip if we've already seen this event
        if event_id_hex in self.seen_events:
            return

        self.seen_events.add(event_id_hex)
        event_kind = ev.kind().as_u16()

        # Process based on event kind
        if (
            event_kind == 5109 and event_id_hex not in self.processing_events
        ):  # Request event
            self.processing_events.add(event_id_hex)
            await self._process_request_event(relay_url, ev)

    async def handle_msg(self, relay_url: str, msg: RelayMessage):
        if msg.as_enum().is_end_of_stored_events():
            print(f"Received EOSE from {relay_url}")

    async def _process_request_event(self, relay_url: str, event: Event):
        """Process a request event (kind 5109) and simulate the payment flow"""
        event_id = event.id().to_hex()
        pubkey = event.author().to_hex()

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
            "pubkey": pubkey,
            "created_at": event.created_at().as_secs(),
        }

        print(
            f"REQUEST RECEIVED: {event_id[:8]}... - {description[:50]}{'...' if len(description) > 50 else ''}"
        )

        # Step 2: Create an invoice for 10 sats using NWC and respond with a kind 7000 event
        print(f"Sending payment required response for request {event_id[:8]}...")

        invoice = None
        payment_hash = None
        if self.nwc:
            try:
                # Create an invoice for 10 sats (10000 msats)
                print(
                    "Attempting to create invoice for 10 sats (10000 msats) using NWC..."
                )
                params = MakeInvoiceRequest(
                    amount=10000,
                    description="Payment for request",
                    description_hash=None,
                    expiry=None,
                )
                print(
                    f"MakeInvoiceRequest params: amount={params.amount} msats, description={params.description}"
                )

                result = await self.nwc.make_invoice(params)
                invoice = result.invoice
                payment_hash = (
                    result.payment_hash
                )  # Store the payment hash for later lookup
                print(f"Successfully created invoice: {invoice[:30]}...")
                print(f"Payment hash: {payment_hash}")
            except Exception as e:
                error_msg = str(e)
                print(f"Error creating invoice: {error_msg}")
                print("Debug information:")
                print(f"  - NWC_KEY environment variable exists: {NWC_KEY is not None}")
                print(f"  - NWC client initialized: {self.nwc is not None}")
                print(f"  - Error type: {type(e).__name__}")

                # Check for specific error messages
                if "Only sat payments are supported" in error_msg:
                    print(
                        "  - This error suggests the wallet only supports payments in satoshis."
                    )
                    print(
                        "  - Ensure the amount is specified in millisatoshis (msats). 10 sats = 10000 msats."
                    )
                    print(
                        "  - Check if your NWC wallet implementation has specific requirements for invoice creation."
                    )

        # Create tags for the payment required event
        tags = [
            Tag.parse(["e", event_id]),  # Reference to the request event
            Tag.parse(["p", pubkey]),  # Reference to the requester's pubkey
            Tag.parse(["status", "payment-required"]),
            Tag.parse(["amount", "10"]),  # 10 sats as specified
        ]

        # Add invoice tag if available
        if invoice:
            tags.append(Tag.parse(["bolt11", invoice]))

        # Build the payment required event
        payment_builder = EventBuilder(
            Kind(7000), "Payment required to process your request"
        ).tags(tags)

        # Send the event using the client
        output = await self.client.send_event_builder(payment_builder)
        payment_event_id = output.id.to_hex()
        print(f"PAYMENT REQUIRED sent: {payment_event_id[:8]}... - Amount: 10 sats")

        # Step 3: Wait for the invoice to be paid
        if invoice and self.nwc and payment_hash:
            print(f"Waiting for invoice payment...")
            payment_confirmed = False
            max_attempts = 10  # Maximum number of attempts to check payment status
            attempt = 0

            while not payment_confirmed and attempt < max_attempts:
                try:
                    # Create lookup request for the invoice with payment_hash
                    lookup_params = LookupInvoiceRequest(
                        invoice=invoice, payment_hash=payment_hash
                    )
                    print(
                        f"Looking up invoice status (attempt {attempt+1}/{max_attempts})..."
                    )

                    # Check invoice status
                    lookup_result = await self.nwc.lookup_invoice(lookup_params)
                    print(f"Invoice lookup result: {lookup_result}")

                    # Check if the invoice is paid
                    if hasattr(lookup_result, "paid") and lookup_result.paid:
                        print(f"Invoice confirmed as paid!")
                        payment_confirmed = True
                    else:
                        print(f"Invoice not yet paid. Waiting...")
                        await asyncio.sleep(2)  # Wait 2 seconds before checking again
                        attempt += 1

                except Exception as e:
                    print(f"Error checking invoice status: {e}")
                    await asyncio.sleep(2)  # Wait 2 seconds before checking again
                    attempt += 1

            if payment_confirmed:
                print(f"Payment confirmed for invoice. Proceeding with job result.")
            else:
                print(
                    f"Payment not confirmed after {max_attempts} attempts. Proceeding anyway for demo purposes."
                )
        else:
            # If no invoice was created or NWC is not available, wait a few seconds
            print(f"No invoice to check. Waiting for payment simulation (3 seconds)...")
            await asyncio.sleep(3)

        # Step 4: Send a kind 6109 job result
        print(f"Sending job result for request {event_id[:8]}...")

        # Sample JSON result data
        result_data = {
            "status": "completed",
            "result": {
                "action": "visual_help_completed",
                "details": "Task completed successfully",
                "timestamp": time.time(),
            },
        }

        # Create tags for the result event
        result_tags = [
            Tag.parse(["e", event_id]),  # Reference to the request event
            Tag.parse(["p", pubkey]),  # Reference to the requester's pubkey
            Tag.parse(["status", "completed"]),
        ]

        # Build the result event
        result_builder = EventBuilder(Kind(6109), json.dumps(result_data)).tags(
            result_tags
        )

        # Send the event using the client
        output = await self.client.send_event_builder(result_builder)
        result_event_id = output.id.to_hex()
        print(f"JOB RESULT sent: {result_event_id[:8]}... - Kind: 6109")
        print(f"Complete flow simulated for request {event_id[:8]}")

        # Remove from processing set
        self.processing_events.remove(event_id)


async def main():
    """Main function to run the payment flow simulator."""
    print("Starting Nostr Payment Flow Simulator")
    print(f"Connecting to relays: {', '.join(RELAY_URLS)}")

    # Generate temporary keys for the simulator
    keys = Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)

    # Connect to relays
    for relay_url in RELAY_URLS:
        await client.add_relay(relay_url.strip())
    await client.connect()

    print(f"Connected to relays with public key: {keys.public_key().to_bech32()}")

    # Create notification handler
    handler = PaymentFlowSimulator(client, keys)

    # Set up filter for events
    # Get events from the last hour
    one_hour_ago = Timestamp.from_secs(Timestamp.now().as_secs() - 3600)

    # Create filter for kind 5109 (request events)
    event_filter = Filter().kinds([Kind(5109)]).since(one_hour_ago)

    # Subscribe to events
    await client.subscribe(event_filter)

    print("Subscribed to events. Waiting for 5109 request events...")
    print("Press Ctrl+C to stop")

    try:
        # Start handling notifications
        await client.handle_notifications(handler)
    except KeyboardInterrupt:
        print("\nStopping payment flow simulator...")
    finally:
        # Disconnect from relays
        await client.disconnect()
        print("Disconnected from relays")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPayment flow simulator stopped")
