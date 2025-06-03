#!/bin/bash
# /agents/cua/start.sh

set -e

echo "🚀 Starting C/ua Agent Environment"
echo "=================================="

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if Lume is installed
if ! command -v lume &> /dev/null; then
    echo "🛠️  Installing Lume CLI..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/lume/scripts/install.sh)"
fi

# Start Lume service if not running
if ! pgrep -f "lume serve" > /dev/null; then
    echo "🌟 Starting Lume service..."
    lume serve &
    sleep 3
fi

# Pull macOS image if not present
if ! lume images | grep -q "macos-sequoia-cua"; then
    echo "💿 Pulling macOS CUA image (this may take a while)..."
    lume pull macos-sequoia-cua:latest
fi

# ADD THIS SECTION: Start the macOS VM
echo "🖥️  Starting macOS VM..."
if ! lume ps | grep -q "macos-sequoia-cua"; then
    echo "🔑 Attempting to start VM with auto-login..."
    
    # Try different methods to start with auto-login
    if lume run macos-sequoia-cua:latest --auto-login 2>/dev/null; then
        echo "✅ VM started with auto-login enabled"
    elif lume run macos-sequoia-cua:latest --headless 2>/dev/null; then
        echo "✅ VM started in headless mode"
    else
        echo "⚠️  Starting VM in standard mode"
        lume run macos-sequoia-cua:latest &
        
        echo ""
        echo "💡 If you encounter a login screen, try these credentials:"
        echo "   Username: cua"
        echo "   Password: password"
        echo "   (or username: user, password: password)"
        echo ""
        echo "🔧 To connect via VNC for manual login:"
        echo "   Run: lume vnc macos-sequoia-cua:latest"
        echo ""
    fi
    
    # Wait for VM to boot
    echo "⏳ Waiting for VM to boot (30 seconds)..."
    sleep 30
    
else
    echo "✅ VM already running"
fi

# Start MCP server in background
echo "🔌 Starting MCP server..."
if command -v cua-mcp-server &> /dev/null; then
    cua-mcp-server &
    MCP_PID=$!
    echo "✅ MCP server started (PID: $MCP_PID)"
else
    echo "⚠️  MCP server not found, continuing without it"
fi

# Start main application
echo "🎨 Starting C/ua Agent with Gradio interface..."
python main.py

# Cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    # Optionally stop the VM on exit
    # lume stop macos-sequoia-cua:latest
}
trap cleanup EXIT