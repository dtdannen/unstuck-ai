# Goose Extension Setup for Unstuck AI

This guide explains how to set up the Unstuck AI extension for Goose, allowing AI agents to request visual help from humans.

## Prerequisites

1. [Goose](https://github.com/block/goose) installed and working
2. Python 3.8+ with pip
3. This repository cloned locally

## Setup Instructions

### 1. Install MCP Server Dependencies

```bash
cd mcp_server/
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `mcp_server/` directory with your credentials:

```bash
# Required for Nostr integration
NOSTR_PRIVATE_KEY=your_nostr_private_key_hex
NWC_KEY=your_nostr_wallet_connect_uri

# Required for screenshot uploads
DIGITAL_OCEAN_SPACES_ACCESS_KEY=your_do_spaces_access_key
DIGITAL_OCEAN_SPACES_SECRET_KEY=your_do_spaces_secret_key
DIGITAL_OCEAN_SPACE_NAME=your_do_space_name

# Optional: Custom relay URLs (defaults provided)
RELAY_URLS=wss://relay.damus.io,wss://relay.nostr.band,wss://relay.primal.net,wss://relay.dvmdash.live
```

### 3. Add Extension to Goose Configuration

1. **Find your Goose config file:**
   - macOS/Linux: `~/.config/goose/config.yaml`
   - Windows: `%APPDATA%\Block\goose\config\config.yaml`

2. **Add the extension configuration:**

   Add this to your `config.yaml` file under the `extensions:` section:

   ```yaml
   extensions:
     unstuckhelper:
       args:
       - /ABSOLUTE/PATH/TO/unstuck-ai/mcp_server/unstuck_ai/server.py
       bundled: false
       cmd: /ABSOLUTE/PATH/TO/unstuck-ai/mcp_server/venv/bin/python
       cwd: /ABSOLUTE/PATH/TO/unstuck-ai/mcp_server
       description: MCP Server for asking human for visual help
       enabled: true
       env_keys: []
       envs: {}
       name: unstuckhelper
       timeout: 300
       type: stdio
   ```

   **Important:** Replace `/ABSOLUTE/PATH/TO/unstuck-ai/` with the actual absolute path to your cloned repository.

### 4. Test the Extension

1. Start Goose:
   ```bash
   goose session --debug
   ```

2. The extension should load without errors. You can test it by asking Goose to:
   ```
   Take a screenshot and use the unstuck helper tool to ask for help
   ```

## Usage

Once configured, you can ask Goose to use the visual helper tool:

- `"Take a screenshot and use the unstuck helper to ask someone to help me click on the Safari icon"`
- `"Use the unstuck helper to ask for help navigating this website"`
- `"Screenshot my screen and ask for help with this captcha"`

## Troubleshooting

### Extension won't start
- Check that all paths in the configuration are absolute paths
- Verify the virtual environment exists: `ls mcp_server/venv/bin/python`
- Check the logs with `goose session --debug`

### Permission errors
- Make sure the virtual environment has the right permissions
- Try recreating the venv: `cd mcp_server && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

### Environment variable issues
- Verify your `.env` file is in the `mcp_server/` directory
- Check that all required environment variables are set

## How It Works

1. **Screenshot**: Goose takes a screenshot of your screen
2. **Upload**: The screenshot is uploaded to Digital Ocean Spaces
3. **Nostr Event**: A help request is broadcast to Nostr relays
4. **Human Response**: Humans bid on the task via the web frontend
5. **Payment**: Lightning payment is made to accept an offer
6. **Instructions**: Human provides click coordinates or instructions
7. **Execution**: Goose receives the instructions and can act on them

## Frontend Setup

For humans to respond to requests, also set up the web frontend:

```bash
cd frontend/
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000` where humans can see and respond to visual help requests.