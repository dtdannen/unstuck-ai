# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### MCP Server

```bash
# Install dependencies for the MCP server
cd mcp_server/
pip install -r requirements.txt

# Run the MCP server in development mode
mcp dev unstuck_ai/server.py

# Run the MCP server via fastmcp (alternative method)
fastmcp run unstuck_ai/server.py:mcp --transport sse

# Monitor Nostr events
python utility/event_monitor.py

# Simulate payment flow (for testing)
python utility/payment_flow_simulator.py
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint the code
npm run lint
```

#### Frontend Dependencies

The frontend uses the following Nostr libraries:
- **NDK (Nostr Development Kit)**: `@nostr-dev-kit/ndk@2.13.3` - Primary Nostr client
- **nostr-tools**: `2.12.0` - Additional Nostr utilities

#### NDK Client Structure

The NDK client is configured in `/frontend/lib/nostr.ts` and provides:
- Automatic relay connection management
- Profile fetching with caching
- Event creation and signing via NIP-07
- Task fetching and real-time subscriptions
- User authentication state management

### Docker

```bash
# Build and run the Docker container
docker-compose up --build

# Stop the Docker container
docker-compose down
```

## Project Architecture

Unstuck AI is a platform that enables AI agents to pay humans to solve visual roadblocks (like captchas, web navigation, computer use) via a Nostr marketplace. The project consists of two main components:

1. **MCP Server**: Acts as a bridge between AI agents (like Goose or Claude) and human operators. It sends requests for visual help through Nostr, processes responses, handles payments via lightning network, and returns results to the AI agent.

2. **Frontend**: A Next.js web application using NDK (Nostr Development Kit) for humans to bid on tasks, complete them, and get paid in Bitcoin satoshis.

### Key Components

- **MCP Server (`mcp_server/unstuck_ai/server.py`)**: The main server implementation that:
  - Provides the `request_visual_help` tool for AI agents
  - Uploads screenshots to Digital Ocean Spaces
  - Creates and broadcasts Nostr events
  - Processes responses and payments
  - Executes actions (mouse clicks, drags) using PyAutoGUI

- **Nostr Integration**: Uses the Nostr protocol for communication:
  - Kind 5109: Help request event
  - Kind 7000: Response event (offers)
  - Kind 6109: Result event

- **Payment System**: Supports lightning payments via:
  - Nostr Wallet Connect (NWC)
  - Lexe API (fallback)

- **Frontend**: Next.js web application that:
  - Uses NDK (Nostr Development Kit) for all Nostr interactions
  - Allows users to login via Nostr (NIP-07 browser extensions)
  - Displays available jobs from Nostr relays
  - Provides a workspace for completing tasks
  - Handles lightning invoice generation and verification
  - Implements real-time event subscriptions via NDK

### Configuration

The application is configured via environment variables in a `.env` file:

- `NOSTR_PRIVATE_KEY`: Private key for the agent's Nostr account
- `NWC_KEY`: Nostr Wallet Connect key for payments
- `RELAY_URLS`: List of Nostr relay URLs
- `DIGITAL_OCEAN_SPACES_ACCESS_KEY`, `DIGITAL_OCEAN_SPACES_SECRET_KEY`, `DIGITAL_OCEAN_SPACE_NAME`: For screenshot uploads

### Docker Integration

The project includes Docker setup that runs both the MCP server and Goose in a virtual desktop environment, making it easy to test and use the system in a self-contained way.

### Workflow

1. AI agent takes a screenshot and calls the `request_visual_help` tool
2. Screenshot is uploaded to Digital Ocean Spaces
3. MCP server creates a Nostr event requesting help
4. Human operators bid on the task with price offers
5. MCP server pays a lightning invoice to accept an offer
6. Human completes the task and sends back instructions
7. MCP server receives the instructions and returns them to the AI agent
8. AI agent can optionally execute the actions (clicks, etc.) via PyAutoGUI