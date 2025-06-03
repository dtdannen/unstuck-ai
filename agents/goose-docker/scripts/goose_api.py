# /agents/goose-docker/scripts/goose_api.py

import asyncio
import json
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os


class GooseSession:
    def __init__(self):
        self.process = None
        self.input_queue = []
        self.output_buffer = []
        self.running = False

    def start_session(self):
        """Start a Goose session"""
        if self.running:
            return "Session already running"

        try:
            # Set display for GUI applications
            os.environ["DISPLAY"] = ":1"

            # Start goose session
            self.process = subprocess.Popen(
                ["goose", "session", "start"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd="/home/goose/workspace",
            )

            self.running = True

            # Start output reader thread
            threading.Thread(target=self._read_output, daemon=True).start()

            # Give it time to start
            time.sleep(2)

            return "Goose session started successfully"

        except Exception as e:
            return f"Error starting Goose: {str(e)}"

    def send_command(self, command):
        """Send a command to Goose"""
        if not self.running or not self.process:
            return "No active Goose session. Please start session first."

        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            # Wait a bit for response
            time.sleep(1)

            # Get recent output
            recent_output = []
            while self.output_buffer:
                recent_output.append(self.output_buffer.pop(0))

            return (
                "\n".join(recent_output) if recent_output else "Command sent to Goose"
            )

        except Exception as e:
            return f"Error sending command: {str(e)}"

    def _read_output(self):
        """Read output from Goose process"""
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_buffer.append(line.strip())
                    # Keep only last 50 lines
                    if len(self.output_buffer) > 50:
                        self.output_buffer.pop(0)
                else:
                    time.sleep(0.1)
            except:
                break

    def get_status(self):
        """Get session status"""
        if self.running and self.process and self.process.poll() is None:
            return "Running"
        else:
            self.running = False
            return "Stopped"


# Global Goose session
goose_session = GooseSession()


class GooseAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.serve_chat_interface()
        elif self.path == "/status":
            self.serve_json({"status": goose_session.get_status()})
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🦆 Goose External Chat Interface</h1>
        
        <div id="status" class="status stopped">
            Status: <span id="status-text">Stopped</span>
        </div>
        
        <button onclick="startSession()">Start Goose Session</button>
        <button onclick="checkStatus()">Check Status</button>
        <a href="http://localhost:6080" target="_blank">
            <button type="button">Open VNC Desktop</button>
        </a>
        
        <div class="chat-log" id="chatLog">Welcome to Goose Chat Interface!
Click "Start Goose Session" to begin, then type commands below.
        </div>
        
        <div class="input-area">
            <input type="text" id="commandInput" placeholder="Type your command for Goose..." 
                   onkeypress="if(event.key==='Enter') sendCommand()">
            <button onclick="sendCommand()">Send Command</button>
        </div>
        
        <div class="examples">
            <h3>💡 Example Commands:</h3>
            <button class="example-btn" onclick="sendExample('Take a screenshot of the desktop')">📸 Screenshot</button>
            <button class="example-btn" onclick="sendExample('Open Firefox and go to google.com')">🌐 Open Browser</button>
            <button class="example-btn" onclick="sendExample('Create a text file called notes.txt')">📝 Create File</button>
            <button class="example-btn" onclick="sendExample('Help me organize files on the desktop')">📁 Organize Files</button>
        </div>
    </div>

    <script>
        function log(message) {
            const chatLog = document.getElementById('chatLog');
            chatLog.textContent += new Date().toLocaleTimeString() + ': ' + message + '\\n';
            chatLog.scrollTop = chatLog.scrollHeight;
        }

        function updateStatus(status) {
            const statusElement = document.getElementById('status');
            const statusText = document.getElementById('status-text');
            statusText.textContent = status;
            statusElement.className = 'status ' + (status === 'Running' ? 'running' : 'stopped');
        }

        async function startSession() {
            log('Starting Goose session...');
            try {
                const response = await fetch('/start', { method: 'POST' });
                const data = await response.json();
                log('Start result: ' + data.result);
                setTimeout(checkStatus, 1000);
            } catch (error) {
                log('Error starting session: ' + error);
            }
        }

        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                updateStatus(data.status);
            } catch (error) {
                log('Error checking status: ' + error);
            }
        }

        async function sendCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            
            if (!command) return;
            
            log('You: ' + command);
            input.value = '';
            
            try {
                const response = await fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                
                const data = await response.json();
                if (data.result) {
                    log('Goose: ' + data.result);
                } else if (data.error) {
                    log('Error: ' + data.error);
                }
            } catch (error) {
                log('Error sending command: ' + error);
            }
        }

        function sendExample(command) {
            document.getElementById('commandInput').value = command;
            sendCommand();
        }

        // Check status on page load
        checkStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def main():
    """Start the API server"""
    server = HTTPServer(("0.0.0.0", 8888), GooseAPIHandler)
    print("🦆 Goose API server starting on port 8888...")
    server.serve_forever()


if __name__ == "__main__":
    main()
