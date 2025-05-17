# MCP Server

The MCP (Master Control Program) Server is responsible for handling visual computer interaction help requests through the Nostr protocol. It acts as a bridge between AI agents needing assistance and human operators who can provide that assistance.

## Features

- Sends kind 51xx events to request visual computer interaction help
- Listens for feedback responses containing prices and lightning invoices
- Allows selection and payment of offers
- Handles receipt of job results

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a .env file based on .env.example:
```
NOSTR_PRIVATE_KEY=your_private_key_here
RELAY_URLS=wss://relay.damus.io,wss://relay.nostr.band
PORT=8000
HOST=0.0.0.0
```

3. Run the server as an MCP server:
```bash
# Development mode
mcp dev mcp_server/server.py

# Or install and run as a package
pip install -e .
unstuck-ai
```

The server will be available as an MCP server that can be used by Goose or other MCP-compatible clients.

## MCP Tools

### request_visual_help
Request visual computer interaction help from humans through Nostr.

Parameters:
- `description`: A detailed description of what help is needed
- `screenshot_url`: URL to a screenshot or image showing the visual context
- `max_price_sats`: Maximum price willing to pay in satoshis 

Returns:
- A dictionary containing the job ID, offers received, selected offer, and result

## Environment Variables

- `NOSTR_PRIVATE_KEY`: Your Nostr private key in hex format
- `RELAY_URLS`: Comma-separated list of Nostr relay URLs
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## Nostr Event Types

### Help Request (Kind 5109)
Sent to request help, includes:
- Description tag
- Image URL tag
- Optional max price tag

### Response (Kind 7000)
Received from helpers, includes:
- Reference to original request event
- Price in sats
- Lightning invoice

### Result (Kind 6000)
Received after payment, includes:
- Reference to original request event
- Result data

## Integration with Goose

To add this MCP server as an extension in Goose:

1. Go to Settings > Extensions > Add
2. Set the Type to StandardIO
3. Provide an ID, name, and description for your extension
4. In the Command field, provide the absolute path to your executable:
   - If installed in development mode: `/path/to/your/python -m mcp dev /path/to/mcp_server/server.py`
   - If installed as a package: `/path/to/your/python -m unstuck-ai`
