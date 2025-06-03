# C/ua Agent Setup

## Quick Start

1. **Set up environment:**
   ```bash
   cd /agents/cua
   chmod +x start.sh
   ```

2. **Configure API keys:**
   - Edit .env file and add your OpenAI API key

3. **Start the agent:**
   bash ./start.sh

4. **Open your browser to:**
   http://localhost:7860

## Usage Examples

### Website Testing

- "Check if my website loads correctly at example.com"
- "Browse to my site and take screenshots of each page"
- "Test the contact form on my website"

### General Computer Tasks

- "Take a screenshot of my desktop"
- "Open Chrome and browse to google.com"
- "Help me organize files on my desktop"
- "Open VS Code and create a new Python file"
- "Find and open the latest file in my Downloads folder"

### Development Tasks

- "Clone a GitHub repository and open it in VS Code"
- "Run a Python script and show me the output"
- "Help me debug this code by running it step by step"

## Configuration

### Environment Variables (.env)

- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key (alternative)
- `CUA_MODEL_PROVIDER` - Choose "OPENAI" or "ANTHROPIC"
- `CUA_MODEL_NAME` - Model to use (e.g., "gpt-4o", "claude-3-opus-20240229")

### MCP Integration

- Edit `config/claude_desktop_config.json` for Claude Desktop integration
- Add custom MCP servers in `mcp-servers/` folder
- Install MCP servers with npm in their respective directories

## Architecture

/agents/cua/
├── .env                          # Environment configuration
├── main.py                       # Main Gradio application
├── start.sh                      # Automated startup script
├── requirements.txt              # Python dependencies
├── config/
│   └── claude_desktop_config.json # MCP server configuration
├── mcp-servers/
│   └── simple-search/            # Example MCP server
└── README.md                     # This file

## Features

- **Visual Interface:** Gradio web UI for chatting with the agent
- **Real-time Monitoring:** Watch the agent work through screenshots
- **MCP Integration:** Works with Claude Desktop and other MCP clients
- **Computer Control:** Full macOS/Linux automation capabilities
- **Multi-model Support:** OpenAI, Anthropic, and local model options

## Troubleshooting

### Common Issues

1. **"Command not found: lume"**
```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/lume/scripts/install.sh)"
```

2. **"No API key found"**
   - Check that your .env file has the correct API key
   - Restart the application after updating .env

3. **"Gradio interface won't start"**
   - Check if port 7860 is available
   - Try: `pip install --upgrade gradio`

4. **"Agent not responding"**
   - Check the terminal logs for error messages
   - Verify your API key has sufficient credits
   - Try switching between OPENAI and ANTHROPIC providers

### Debug Commands

# Check Lume status
lume status

# View running containers
lume ps

# Check Python environment
pip list | grep cua

# Test API connection
python -c "import openai; print('OpenAI imported successfully')"