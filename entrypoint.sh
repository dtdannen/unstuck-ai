#!/bin/bash
set -e

# Start virtual display
./ui/xvfb_startup.sh

# Start window manager and panel
./ui/tint2_startup.sh
./ui/mutter_startup.sh

# Start VNC server
./ui/x11vnc_startup.sh

# Start noVNC
./ui/novnc_startup.sh

# Start MCP server in the background
cd $HOME/mcp_server
fastmcp run unstuck_ai/server.py:mcp --transport sse &
MCP_PID=$!

# Create a welcome message and instructions
cat > $HOME/welcome.txt << EOL
Welcome to Unstuck AI Docker Container!

To interact with Goose:
1. Open a terminal (right-click on desktop and select "Terminal")
2. Run the command: goose session --with-remote-extension http://127.0.0.1:8000/sse

The MCP server is already running in the background.
EOL

# Open a terminal with the welcome message
DISPLAY=:${DISPLAY_NUM} xfce4-terminal --geometry=80x24+10+10 --title="Welcome to Unstuck AI" --command="cat $HOME/welcome.txt" &

echo "✨ Unstuck AI Container is ready!"
echo "➡️  Access the desktop via VNC at http://localhost:6080/vnc.html"
echo "➡️  The MCP server is running at http://localhost:8000"

# Keep the container running
wait $MCP_PID
