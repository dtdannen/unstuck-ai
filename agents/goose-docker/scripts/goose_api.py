# /agents/goose-docker/scripts/goose_api.py

import asyncio
import json
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import signal
import re


def strip_ansi_codes(text):
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


class GooseSession:
    def __init__(self):
        self.process = None
        self.input_queue = []
        self.output_buffer = []
        self.running = False
        self.last_output_time = time.time()

    def start_session(self):
        """Start a Goose session with Computer Controller enabled"""
        if self.running and self.process and self.process.poll() is None:
            return "Session already running"

        try:
            # Set display for GUI applications
            os.environ["DISPLAY"] = ":1"
            # Set the environment variable that computer toolkit checks for
            os.environ[":1"] = "true"
            # Set Goose provider and model
            os.environ["GOOSE_PROVIDER"] = "anthropic"
            os.environ["GOOSE_MODEL"] = "claude-opus-4-20250514"

            # Set up unstuck server environment variables
            if "NOSTR_PRIVATE_KEY" in os.environ:
                os.environ["NOSTR_PRIVATE_KEY"] = os.environ["NOSTR_PRIVATE_KEY"]
            if "NWC_KEY" in os.environ:
                os.environ["NWC_KEY"] = os.environ["NWC_KEY"]
            if "RELAY_URLS" in os.environ:
                os.environ["RELAY_URLS"] = os.environ["RELAY_URLS"]
            if "DIGITAL_OCEAN_SPACES_ACCESS_KEY" in os.environ:
                os.environ["DIGITAL_OCEAN_SPACES_ACCESS_KEY"] = os.environ[
                    "DIGITAL_OCEAN_SPACES_ACCESS_KEY"
                ]
            if "DIGITAL_OCEAN_SPACES_SECRET_KEY" in os.environ:
                os.environ["DIGITAL_OCEAN_SPACES_SECRET_KEY"] = os.environ[
                    "DIGITAL_OCEAN_SPACES_SECRET_KEY"
                ]
            if "DIGITAL_OCEAN_SPACE_NAME" in os.environ:
                os.environ["DIGITAL_OCEAN_SPACE_NAME"] = os.environ[
                    "DIGITAL_OCEAN_SPACE_NAME"
                ]

            # Ensure config directory exists
            config_dir = "/home/goose/.config/goose"
            os.makedirs(config_dir, exist_ok=True)

            # Set API key in environment for this session
            if "ANTHROPIC_API_KEY" in os.environ:
                print(
                    f"🔑 Using Anthropic API key: {os.environ['ANTHROPIC_API_KEY'][:8]}..."
                )
            else:
                return "ERROR: ANTHROPIC_API_KEY not set in environment"

            # Start goose session with just the unstuck MCP extension (no built-in computer for now)
            cmd = [
                "goose",
                "session",
                "--with-extension",
                "fastmcp run /home/goose/mcp_server/unstuck_ai/server.py:mcp --transport stdio",
            ]

            print(f"🚀 Starting Goose with command: {' '.join(cmd)}")
            print(
                f"🔧 Using unstuck MCP server via CLI flags (testing without built-in computer extension)"
            )

            # Check if MCP servers config exists
            mcp_config_path = "/home/goose/.config/goose/mcp_servers.json"
            if os.path.exists(mcp_config_path):
                print(f"✅ MCP config found at {mcp_config_path}")
            else:
                print(f"❌ Warning: MCP config not found at {mcp_config_path}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd="/home/goose/workspace",
                env=os.environ.copy(),
                preexec_fn=os.setsid,  # Create new process group
            )

            # Start output reader thread
            threading.Thread(target=self._read_output, daemon=True).start()

            # Wait a bit and check if process is still alive
            time.sleep(3)

            if self.process.poll() is not None:
                # Process has already exited
                return_code = self.process.returncode
                error_output = "".join(self.output_buffer)
                return f"ERROR: Goose process exited with code {return_code}. Output: {error_output}"

            self.running = True
            self.last_output_time = time.time()

            # Give it more time to fully initialize
            time.sleep(2)

            # Send a test command to check available tools
            self.process.stdin.write("list tools\n")
            self.process.stdin.flush()
            time.sleep(2)

            return "Goose session started successfully with Unstuck MCP extension"

        except FileNotFoundError:
            return (
                "ERROR: 'goose' command not found. Please ensure goose-ai is installed."
            )
        except Exception as e:
            return f"ERROR starting Goose: {str(e)}"

    def send_command(self, command):
        """Send a command to Goose (non-blocking)"""
        if not self.running or not self.process:
            return "No active Goose session. Please start session first."

        # Check if process is still alive
        if self.process.poll() is not None:
            self.running = False
            return_code = self.process.returncode
            error_output = "".join(self.output_buffer[-10:])
            return f"Goose session died (exit code: {return_code}). Recent output: {error_output}. Please restart session."

        try:
            if command.strip():  # Only send non-empty commands
                print(f"📝 Sending command to Goose: {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
                return f"Command sent: {command}"
            else:
                # Just return recent output for polling
                recent_lines = self.output_buffer[-20:] if self.output_buffer else []
                return "\n".join(recent_lines)

        except BrokenPipeError:
            self.running = False
            return "Connection to Goose lost. Please restart session."
        except Exception as e:
            return f"Error sending command: {str(e)}"

    def _read_output(self):
        """Read output from Goose process"""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    # Strip ANSI color codes for clean web display
                    clean_line = strip_ansi_codes(line)
                    print(f"📥 Goose output: {clean_line}")  # Debug logging
                    self.output_buffer.append(clean_line)
                    self.last_output_time = time.time()

                    # Keep only last 100 lines to prevent memory issues
                    if len(self.output_buffer) > 100:
                        self.output_buffer = self.output_buffer[-50:]
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error reading output: {e}")
                break

        print("📊 Output reader thread ended")

    def get_status(self):
        """Get session status"""
        if self.process is None:
            return "Not started"
        elif self.process.poll() is None and self.running:
            return "Running"
        else:
            self.running = False
            return f"Stopped (exit code: {self.process.returncode if self.process else 'unknown'})"

    def stop_session(self):
        """Stop the Goose session"""
        if self.process:
            try:
                # Try graceful shutdown first
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                time.sleep(2)

                # Force kill if still alive
                if self.process.poll() is None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)

            except:
                pass

        self.running = False
        self.process = None
        return "Session stopped"


# Global Goose session
goose_session = GooseSession()


class GooseAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.serve_chat_interface()
        elif self.path == "/status":
            self.serve_json({"status": goose_session.get_status()})
        elif self.path == "/poll":
            # Get recent output for polling
            recent_output = (
                goose_session.output_buffer[-50:] if goose_session.output_buffer else []
            )
            self.serve_json(
                {
                    "output": recent_output,
                    "running": goose_session.running,
                    "buffer_size": len(goose_session.output_buffer),
                }
            )
        elif self.path == "/debug":
            # Your existing debug endpoint
            debug_info = {
                "running": goose_session.running,
                "process_alive": goose_session.process is not None
                and goose_session.process.poll() is None,
                "recent_output": (
                    goose_session.output_buffer[-10:]
                    if goose_session.output_buffer
                    else []
                ),
                "env_vars": {
                    "DISPLAY": os.environ.get("DISPLAY"),
                    "ANTHROPIC_API_KEY": (
                        "SET" if os.environ.get("ANTHROPIC_API_KEY") else "NOT SET"
                    ),
                    "HOME": os.environ.get("HOME"),
                    "PWD": os.getcwd(),
                },
            }
            self.serve_json(debug_info)
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/start":
            result = goose_session.start_session()
            self.serve_json({"result": result})
        elif self.path == "/command":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(post_data)
            command = data.get("command", "")

            if command:
                result = goose_session.send_command(command)
                self.serve_json({"result": result, "command": command})
            else:
                self.serve_json({"error": "No command provided"})
        else:
            self.send_error(404)

    def serve_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_chat_interface(self):
        """Serve the chat interface HTML"""
        html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>🦆 Goose Chat Interface</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .chat-log { 
                height: 400px; 
                border: 1px solid #ccc; 
                padding: 10px; 
                overflow-y: scroll; 
                background: #f9f9f9;
                margin-bottom: 10px;
                font-family: monospace;
                white-space: pre-wrap;
            }
            .input-area { 
                display: flex; 
                gap: 10px; 
                margin-top: 10px;
            }
            input[type="text"] { 
                flex: 1; 
                padding: 10px; 
                border: 1px solid #ccc; 
                border-radius: 5px;
            }
            button { 
                padding: 10px 20px; 
                background: #007bff; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;
            }
            button:hover { background: #0056b3; }
            .status { 
                margin-bottom: 10px; 
                padding: 10px; 
                border-radius: 5px;
            }
            .status.running { background: #d4edda; border: 1px solid #c3e6cb; }
            .status.stopped { background: #f8d7da; border: 1px solid #f5c6cb; }
            .examples { 
                margin-top: 20px; 
                padding: 15px; 
                background: #e9ecef; 
                border-radius: 5px;
            }
            .example-btn {
                margin: 5px;
                padding: 5px 10px;
                background: #28a745;
                font-size: 12px;
            }
            .polling-status {
                font-size: 12px;
                color: #666;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🦆 Goose External Chat Interface</h1>
            
            <div id="status" class="status stopped">
                Status: <span id="status-text">Stopped</span>
                <span id="polling-status" class="polling-status"></span>
            </div>

            <button onclick="startSession()">Start Goose Session</button>
            <button onclick="checkStatus()">Check Status</button>
            <a href="http://localhost:6080" target="_blank">
                <button type="button">Open VNC Desktop</button>
            </a>
            <button onclick="resetOutput()">🔄 Reset & Show All</button>

            <div class="chat-log" id="chatLog">Welcome to Goose Chat Interface!<br>Click "Start Goose Session" to begin, then type commands below.</div>
            
            <div class="input-area">
                <input type="text" id="commandInput" placeholder="Type your command for Goose..." onkeypress="if(event.key==='Enter') sendCommand()">
                <button onclick="sendCommand()">Send Command</button>
            </div>
            
            <div class="examples">
                <h3>💡 Example Commands:</h3>
                <button class="example-btn" onclick="sendExample('Take a screenshot of the desktop')">📸 Screenshot</button>
                <button class="example-btn" onclick="sendExample('Open Firefox and go to google.com')">🌐 Open Browser</button>
                <button class="example-btn" onclick="sendExample('Create a text file called notes.txt')">📝 Create File</button>
                <button class="example-btn" onclick="sendExample('can you take a screenshot yourself, save it to a file and note the filename, and then ask a human via unstuck visual helper tool to help you figure out where to click to open the web browser application on the desktop?')">Run Unstuck Demo</button>
            </div>
        </div>

        <script>
            let lastBufferSize = 0;
            let pollingInterval = null;
            let isPolling = false;

            function log(message) {
                const chatLog = document.getElementById('chatLog');
                chatLog.textContent += new Date().toLocaleTimeString() + ': ' + message + '\\n';
                chatLog.scrollTop = chatLog.scrollHeight;
            }

            function updateStatus(status) {
                const statusElement = document.getElementById('status');
                const statusText = document.getElementById('status-text');
                const pollingStatus = document.getElementById('polling-status');
                
                statusText.textContent = status;
                statusElement.className = 'status ' + (status === 'Running' ? 'running' : 'stopped');
                
                // Update polling status indicator
                if (isPolling) {
                    pollingStatus.textContent = '🔄 Live updates active';
                } else {
                    pollingStatus.textContent = '';
                }
            }

            function resetOutput() {
                lastBufferSize = 0;
                log('🔄 Reset - will show all output');
            }

            async function startSession() {
                console.log('🔍 startSession() called');
                log('Starting Goose session...');
                
                try {
                    console.log('🔍 About to make fetch request to /start');
                    const response = await fetch('/start', { method: 'POST' });
                    console.log('🔍 Got response:', response);
                    
                    const data = await response.json();
                    console.log('🔍 Response data:', data);
                    
                    log('Start result: ' + data.result);
                    
                    // Auto-start polling when session starts
                    setTimeout(() => {
                        checkStatus();
                        startPolling();
                    }, 1000);
                    
                } catch (error) {
                    console.error('🔍 Error in startSession:', error);
                    log('Error starting session: ' + error);
                }
            }

            async function checkStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    updateStatus(data.status);
                    
                    // Auto-manage polling based on status
                    if (data.status === 'Running' && !isPolling) {
                        startPolling();
                    } else if (data.status !== 'Running' && isPolling) {
                        stopPolling();
                    }
                    
                } catch (error) {
                    log('Error checking status: ' + error);
                }
            }

            function startPolling() {
                if (pollingInterval) return; // Already polling
                
                isPolling = true;
                updateStatus(document.getElementById('status-text').textContent); // Refresh status display
                
                pollingInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/poll');
                        const data = await response.json();
                        
                        // Show new output
                        if (data.buffer_size > lastBufferSize) {
                            const newLines = data.output.slice(-(data.buffer_size - lastBufferSize));
                            if (newLines.length > 0) {
                                log('Goose: ' + newLines.join('\\n'));
                            }
                            lastBufferSize = data.buffer_size;
                        }
                        
                        // Auto-stop polling if session ends
                        if (!data.running && isPolling) {
                            log('⚠️ Goose session ended');
                            stopPolling();
                        }
                        
                    } catch (error) {
                        console.log('Polling error:', error);
                    }
                }, 1000); // Poll every 1 second
            }

            function stopPolling() {
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    isPolling = false;
                    updateStatus(document.getElementById('status-text').textContent); // Refresh status display
                }
            }

            async function sendCommand() {
                const input = document.getElementById('commandInput');
                const command = input.value.trim();
                
                if (!command) return;
                
                log('You: ' + command);
                input.value = '';
                
                // Auto-start polling if not already active (shouldn't be needed, but just in case)
                if (!isPolling) {
                    startPolling();
                }
                
                try {
                    const response = await fetch('/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: command })
                    });
                    
                    const data = await response.json();
                    
                } catch (error) {
                    log('Error sending command: ' + error);
                }
            }

            function sendExample(command) {
                document.getElementById('commandInput').value = command;
                sendCommand();
            }

            // Initialize
            checkStatus();
            
            // Check status periodically to auto-manage polling
            setInterval(checkStatus, 30000);
        </script>
    </body>
    </html>
    """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def main():
    """Start the API server"""
    server = HTTPServer(("0.0.0.0", 8888), GooseAPIHandler)
    print("🦆 Goose API server starting on port 8888...")
    server.serve_forever()


if __name__ == "__main__":
    main()
