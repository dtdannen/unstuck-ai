# Helpful Scripts for Testing

## event_monitor.py

Use this to watch all nostr events going back and forth between the AI MCP Server and the humans bidding and working on tasks. Streams all kind 5109, 6109, and 7000 events as it sees them.

## test_do_spaces_upload.py

Use this to test uploading to your digital ocean spaces. Requires the environment variables in the `.env.example` are correct.

## payment_flow_simulator.py

This simulates a human bidding and doing work on a task, so you can quickly test and work on the MCP server without having real humans do work.