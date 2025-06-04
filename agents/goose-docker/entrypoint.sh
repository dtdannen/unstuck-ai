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

# Set for current session too
export GOOSE_DISABLE_KEYRING=1
export GOOSE_DEBUG=1
export GOOSE_SANDBOX_MODE=true
export GOOSE_ALLOW_SUDO=true
export DISABLE_SAFETY_CHECKS=true

# Copy MCP server configuration to home directory
echo "📋 Setting up MCP server configuration..."
if [ -f /home/goose/.config/mcp_servers.json ]; then
    echo "MCP server config already exists"
else
    mkdir -p /home/goose/.config
    cp /home/goose/.config/goose/mcp_servers.json /home/goose/.config/mcp_servers.json 2>/dev/null || echo "Note: mcp_servers.json not found in goose config"
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
if [ -f /home/goose/.config/mcp_servers.json ]; then
    cat /home/goose/.config/mcp_servers.json
else
    echo "MCP servers config not found!"
fi
echo ""
echo "🔍 Checking MCP server files:"
ls -la /home/goose/mcp_server/ 2>/dev/null || echo "MCP server directory not found"
echo ""
# Test if the flagging issue is resolved
echo "🧪 Testing sudo command flagging..."
echo "Test: sudo apt update" | goose session --no-session 2>&1 | head -10
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

# Test sudo commands
echo "🧪 Testing sudo commands..."
goose session --no-session -i <(echo "run: sudo apt update") || echo "Command still flagged"

# Start unstuck MCP server first (like in local setup)
echo "🚀 Starting unstuck MCP server..."
cd /home/goose/mcp_server
fastmcp run unstuck_ai/server.py:mcp --transport sse &
MCP_PID=$!
sleep 5
echo "✅ Unstuck MCP server started on port 8000"

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
    
    # Check MCP server
    if ! kill -0 $MCP_PID 2>/dev/null; then
        echo "⚠️  MCP server died, restarting..."
        cd /home/goose/mcp_server
        fastmcp run unstuck_ai/server.py:mcp --transport sse &
        MCP_PID=$!
    fi
    
    # Check API
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "⚠️  Goose API died, restarting..."
        python3 /home/goose/scripts/goose_api.py &
        API_PID=$!
    fi
done