#!/bin/bash

# Setup script for Unstuck AI Goose extension
set -e

echo "🦆 Setting up Unstuck AI extension for Goose..."

# Get the absolute path to this repository
REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Repository path: $REPO_PATH"

# Check if Goose config directory exists
GOOSE_CONFIG_DIR="$HOME/.config/goose"
GOOSE_CONFIG_FILE="$GOOSE_CONFIG_DIR/config.yaml"

if [ ! -d "$GOOSE_CONFIG_DIR" ]; then
    echo "❌ Goose config directory not found at $GOOSE_CONFIG_DIR"
    echo "Please install and run Goose at least once to create the config directory."
    exit 1
fi

# Install MCP server dependencies
echo "📦 Installing MCP server dependencies..."
cd "$REPO_PATH/mcp_server"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env template if it doesn't exist
ENV_FILE="$REPO_PATH/mcp_server/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env template..."
    cat > "$ENV_FILE" << 'EOF'
# Required for Nostr integration
NOSTR_PRIVATE_KEY=your_nostr_private_key_hex
NWC_KEY=your_nostr_wallet_connect_uri

# Required for screenshot uploads
DIGITAL_OCEAN_SPACES_ACCESS_KEY=your_do_spaces_access_key
DIGITAL_OCEAN_SPACES_SECRET_KEY=your_do_spaces_secret_key
DIGITAL_OCEAN_SPACE_NAME=your_do_space_name

# Optional: Custom relay URLs (defaults provided)
RELAY_URLS=wss://relay.damus.io,wss://relay.nostr.band,wss://relay.primal.net,wss://relay.dvmdash.live
EOF
    echo "⚠️  Please edit $ENV_FILE with your actual credentials"
fi

# Check if extension already exists in config
if grep -q "unstuckhelper:" "$GOOSE_CONFIG_FILE" 2>/dev/null; then
    echo "⚠️  unstuckhelper extension already exists in $GOOSE_CONFIG_FILE"
    echo "Please manually update the paths if needed."
else
    echo "📝 Adding extension to Goose config..."
    
    # Create backup
    cp "$GOOSE_CONFIG_FILE" "$GOOSE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add extension configuration
    cat >> "$GOOSE_CONFIG_FILE" << EOF
  unstuckhelper:
    args:
    - $REPO_PATH/mcp_server/unstuck_ai/server.py
    bundled: false
    cmd: $REPO_PATH/mcp_server/venv/bin/python
    cwd: $REPO_PATH/mcp_server
    description: MCP Server for asking human for visual help
    enabled: true
    env_keys: []
    envs: {}
    name: unstuckhelper
    timeout: 300
    type: stdio
EOF
    echo "✅ Extension added to Goose config"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit $ENV_FILE with your actual credentials"
echo "2. Run 'goose session' to test the extension"
echo "3. Ask Goose: 'Take a screenshot and use the unstuck helper tool to ask for help'"
echo ""
echo "For more information, see GOOSE_SETUP.md"