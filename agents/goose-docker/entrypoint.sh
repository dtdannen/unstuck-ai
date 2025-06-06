#!/bin/bash
# /agents/goose-docker/entrypoint.sh

echo "🚀 Starting Goose Docker Environment"
echo "==================================="

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up services..."
    pkill -f websockify 2>/dev/null || true
    pkill -f goose_api.py 2>/dev/null || true
    vncserver -kill :1 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Set environment variables for the session
export USER=goose
export HOME=/home/goose
export DISPLAY=:1
export PATH="$HOME/.local/bin:$PATH"

# Set API keys globally for all terminal sessions
echo "🔑 Setting up API keys..."
echo "export OPENAI_API_KEY='${OPENAI_API_KEY}'" >> ~/.bashrc
echo "export ANTHROPIC_API_KEY='${ANTHROPIC_API_KEY}'" >> ~/.bashrc

# Also set for current session
export OPENAI_API_KEY="${OPENAI_API_KEY}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"

# Set additional goose environment variables
echo "🔧 Setting up goose environment variables..."
echo "export GOOSE_DISABLE_KEYRING=1" >> ~/.bashrc
echo "export GOOSE_DEBUG=1" >> ~/.bashrc
echo "export GOOSE_SANDBOX_MODE=true" >> ~/.bashrc
echo "export GOOSE_ALLOW_SUDO=true" >> ~/.bashrc
echo "export DISABLE_SAFETY_CHECKS=true" >> ~/.bashrc
echo "export GOOSE_PROVIDER=anthropic" >> ~/.bashrc
echo "export GOOSE_MODEL=claude-opus-4-20250514" >> ~/.bashrc

# Set for current session too
export GOOSE_DISABLE_KEYRING=1
export GOOSE_DEBUG=1
export GOOSE_SANDBOX_MODE=true
export GOOSE_ALLOW_SUDO=true
export DISABLE_SAFETY_CHECKS=true
export GOOSE_PROVIDER=anthropic
export GOOSE_MODEL=claude-opus-4-20250514

# Check MCP server configuration
echo "📋 Checking MCP server configuration..."
# Block's Goose looks for MCP servers in ~/.config/goose/mcp_servers.json
if [ -f /home/goose/.config/goose/mcp_servers.json ]; then
    echo "✅ MCP server config found at ~/.config/goose/mcp_servers.json"
    # Note: Goose should handle environment variable expansion in the JSON file
else
    echo "❌ Warning: mcp_servers.json not found at ~/.config/goose/mcp_servers.json"
fi

echo "🔍 Checking goose configuration..."
goose configure --help 2>/dev/null || echo "Note: 'goose configure' command not available"
echo ""
echo "🔍 Checking goose session options..."
goose session --help
echo ""
echo "🔍 Checking goose help for MCP info..."
goose --help | grep -i mcp || echo "No MCP info in main help"
echo ""
echo "🔍 Current goose profiles:"
cat ~/.config/goose/profiles.yaml
echo ""
echo "📋 MCP servers configuration:"
if [ -f /home/goose/.config/goose/mcp_servers.json ]; then
    echo "Found at ~/.config/goose/mcp_servers.json:"
    cat /home/goose/.config/goose/mcp_servers.json
else
    echo "MCP servers config not found at ~/.config/goose/mcp_servers.json!"
fi
echo ""
echo "🔍 Checking MCP server files:"
ls -la /home/goose/mcp_server/ 2>/dev/null || echo "MCP server directory not found"
echo ""
echo "🔍 Checking if fastmcp is available:"
which fastmcp || echo "fastmcp not found in PATH"
echo ""
echo "🔍 Checking if goose-mcp-server is available:"
which goose-mcp-server || echo "goose-mcp-server not found in PATH"
echo ""
# Skip outdated test - goose session syntax has changed
echo ""
echo "🧹 Cleaning any existing VNC sessions..."
vncserver -kill :1 2>/dev/null || echo "No existing VNC sessions"

echo "🖥️  Starting VNC server..."
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no -SecurityTypes VncAuth

sleep 5

if pgrep Xtigervnc > /dev/null; then
    echo "✅ VNC server started successfully"
    
    # Now test unstuck server after VNC is running
    echo "🔍 Testing if unstuck MCP server can run now that display is available:"
    cd /home/goose/mcp_server && python3 -c "import unstuck_ai.server; print('✅ Unstuck module imports successfully')" 2>&1 || echo "❌ Failed to import unstuck server"
    cd /home/goose
    echo ""
else
    echo "❌ VNC server failed to start"
    exit 1
fi

echo "🌐 Starting noVNC..."
websockify --web=/usr/share/novnc/ 6080 localhost:5901 &
NOVNC_PID=$!

sleep 3

# test automation works
echo "🧪 Testing automation capabilities..."
python3 /home/goose/scripts/test_automation.py

if [ $? -eq 0 ]; then
    echo "✅ Automation test passed!"
else
    echo "⚠️  Automation test had issues, but continuing..."
fi

# Test browser availability
echo "🌐 Testing browser availability..."
if command -v firefox &> /dev/null; then
    echo "✅ Firefox is installed at: $(which firefox)"
else
    echo "❌ Firefox not found!"
fi

# Skip outdated sudo test - command syntax has changed

# Unstuck MCP server is now configured in mcp_servers.json
# and will be started automatically by Goose
echo "✅ Unstuck MCP configured in mcp_servers.json"

# Start external Goose API
echo "🦆 Starting external Goose API..."
python3 /home/goose/scripts/goose_api.py &
API_PID=$!

echo "✅ All services started!"
echo ""
echo "🌐 Access points:"
echo "   External Chat:  http://localhost:8888"
echo "   noVNC Desktop:  http://localhost:6080"
echo "   VNC Client:     vnc://localhost:5901"
echo "   Password:       password"
echo ""
echo "🦆 Goose is ready!"
echo "   API Key: ${OPENAI_API_KEY:0:8}..." # Show first 8 chars
echo ""

# Keep container running
while true; do
    sleep 60
    
    # Check VNC
    if ! pgrep Xtigervnc > /dev/null; then
        echo "⚠️  VNC died, restarting..."
        vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
    fi
    
    # Check noVNC
    if ! kill -0 $NOVNC_PID 2>/dev/null; then
        echo "⚠️  noVNC died, restarting..."
        websockify --web=/usr/share/novnc/ 6080 localhost:5901 &
        NOVNC_PID=$!
    fi
    
    # MCP servers are managed by Goose itself via mcp_servers.json
    
    # Check API
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "⚠️  Goose API died, restarting..."
        python3 /home/goose/scripts/goose_api.py &
        API_PID=$!
    fi
done